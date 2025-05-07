from django.apps import AppConfig
from django.db.models.signals import post_migrate

class UauthConfig(AppConfig):
    name = 'core.uauth'

    def ready(self):
        from .signals import create_user_groups_and_permissions
        from django.db.models.signals import post_migrate
        post_migrate.connect(create_user_groups_and_permissions, sender=self)