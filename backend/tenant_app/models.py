from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models
from encrypted_model_fields.fields import EncryptedTextField
from django.contrib.postgres.fields import ArrayField


class UserCryptoProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    private_key = EncryptedTextField()
    public_key = models.TextField()

    signature_embedding = ArrayField(
        models.FloatField(),
        size=2048,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"Crypto Profile - {self.user.username}"

class SignedDocument(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='signatures')

    file_name = models.TextField()
    checksum = models.CharField(max_length=64, db_index=True)
    signature = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Signed Documents - {self.user.username}"

def generate_key_pair():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode('utf-8')

    public_key = private_key.public_key()
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode('utf-8')

    return private_pem, public_pem


@receiver(post_save, sender=User)
def create_crypto_profile(sender, instance, created, **kwargs):
    if created:
        private_key, public_key = generate_key_pair()
        UserCryptoProfile.objects.create(
            user=instance,
            private_key=private_key,
            public_key=public_key
        )