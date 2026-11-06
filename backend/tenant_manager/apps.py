from django.apps import AppConfig


class PublicAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tenant_manager'
