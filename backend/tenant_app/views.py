import base64
from io import BytesIO

import numpy as np
import torch
from PIL import Image
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_public_key, load_pem_private_key
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from ai_module.ai_service import get_feature_vector
from tenant_app.models import UserCryptoProfile, SignedDocument


class SignView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        file_name = request.data.get('file_name')
        checksum = request.data.get('checksum')
        img_b64 = request.data.get('signature_image')

        if not checksum or not img_b64:
            return Response({'error': 'Brak danych (checksum lub podpis)'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            crypto_profile = UserCryptoProfile.objects.get(user=request.user)
        except UserCryptoProfile.DoesNotExist:
            return Response({'error': 'Profil kryptograficzny nie istnieje'}, status=status.HTTP_404_NOT_FOUND)

        try:
            if "," in img_b64:
                img_b64 = img_b64.split(",")[1]

            img_data = base64.b64decode(img_b64)
            pil_image = Image.open(BytesIO(img_data)).convert("L")
            img_array = np.array(pil_image)

            new_embedding_np = get_feature_vector(img_array)

            new_embedding = new_embedding_np.flatten()

        except Exception as e:
            return Response({'error': f'Błąd podczas przetwarzania podpisu przez AI: {str(e)}'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        new_embedding_tensor = torch.tensor(new_embedding, dtype=torch.float32)

        if not hasattr(crypto_profile, "signature_embedding") or crypto_profile.signature_embedding is None:
            crypto_profile.signature_embedding = new_embedding.tolist()
            crypto_profile.save()
        else:
            stored_embedding = torch.tensor(crypto_profile.signature_embedding, dtype=torch.float32)

            dist = torch.norm(stored_embedding - new_embedding_tensor).item()

            if dist > 5.0:
                return Response(
                    {'error': f'Podpis odrzucony. Zbyt duża różnica (dystans={dist:.2f} > 5.0)'},
                    status=status.HTTP_403_FORBIDDEN
                )

        try:
            private_key_bytes = crypto_profile.private_key.encode("utf-8")
            private_key = load_pem_private_key(private_key_bytes, password=None, backend=default_backend())

            checksum_bytes = checksum.encode('utf-8')
            signature = private_key.sign(
                checksum_bytes,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            signature_b64 = base64.b64encode(signature).decode('utf-8')
        except Exception as e:
            return Response({'error': f'Błąd podpisywania: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        SignedDocument.objects.create(
            user=crypto_profile.user,
            file_name=file_name,
            checksum=checksum,
            signature=signature_b64
        )

        return Response({
            'user_id': crypto_profile.user.id,
            'username': crypto_profile.user.username,
            'signature': signature_b64,
        }, status=status.HTTP_200_OK)


class VerifySignaturesView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        signatures_data = request.data.get('signatures', [])
        checksum = request.data.get('checksum')

        if not signatures_data:
            return Response({'error': 'Brak signatures'}, status=status.HTTP_400_BAD_REQUEST)

        if not checksum:
            return Response({'error': 'Brak checksum'}, status=status.HTTP_400_BAD_REQUEST)

        results = []
        checksum_bytes = checksum.encode('utf-8')

        for sig_data in signatures_data:
            user_id = sig_data.get('user_id')
            signature_b64 = sig_data.get('signature')

            if not user_id or not signature_b64:
                results.append({
                    'user_id': user_id,
                    'valid': False,
                    'error': 'Brakujące dane'
                })
                continue

            try:
                user = User.objects.get(id=user_id)
                crypto_profile = UserCryptoProfile.objects.get(user=user)

                public_key_pem = crypto_profile.public_key.encode('utf-8')
                public_key = load_pem_public_key(public_key_pem, backend=default_backend())

                signature = base64.b64decode(signature_b64)

                public_key.verify(
                    signature,
                    checksum_bytes,
                    padding.PSS(
                        mgf=padding.MGF1(hashes.SHA256()),
                        salt_length=padding.PSS.MAX_LENGTH
                    ),
                    hashes.SHA256()
                )

                results.append({
                    'user_id': user_id,
                    'valid': True,
                    'username': user.username
                })

            except User.DoesNotExist:
                results.append({
                    'user_id': user_id,
                    'valid': False,
                    'error': 'Użytkownik nie istnieje'
                })
            except UserCryptoProfile.DoesNotExist:
                results.append({
                    'user_id': user_id,
                    'valid': False,
                    'error': 'Brak profilu kryptograficznego'
                })
            except (InvalidSignature, ValueError) as e:
                results.append({
                    'user_id': user_id,
                    'valid': False,
                    'error': f'Nieprawidłowy podpis: {str(e)}'
                })
            except Exception as e:
                results.append({
                    'user_id': user_id,
                    'valid': False,
                    'error': f'Błąd weryfikacji: {str(e)}'
                })

        all_valid = all(result['valid'] for result in results)

        return Response({
            'checksum': checksum,
            'all_signatures_valid': all_valid,
            'verification_results': results
        }, status=status.HTTP_200_OK)