#This class is needed, because if I describe permissions in apps.py, because it will try to
# perform database operations(like adding permissions and groups) before the Django app 
# registry is fully initialized. By using a signal I ensure that the groups and permissions 
# are created after all migrations have been applied

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_migrate
from django.apps import AppConfig

User = get_user_model()

def create_user_groups_and_permissions(sender, **kwargs):
    
    try:
        order_content_type = ContentType.objects.get(app_label='orders', model='order')
    except ContentType.DoesNotExist:
        # ContentType doesn't exist yet, so we can't create the permissions
        # This will happen during initial migrations
        print("Warning: ContentType for orders.order not found. Skipping permission creation.")
        return

    groups_permissions = {
        'Regular': [
            'add_order',
            'change_order',
            'delete_order',
            'view_order',
        ],
        'Agency': [
            'add_order',
            'change_order',
            'delete_order',
            'view_order',
            'add_evaluator',
            'view_evaluator_orders',
        ],
        'Evaluator': [
            'add_order',
            'change_order',
            'delete_order',
            'view_order',
            'evaluate_order',
        ],
    }

    for group_name, perm_codes in groups_permissions.items():
        group, created = Group.objects.get_or_create(name=group_name)
        
        for perm_code in perm_codes:
            perm, created = Permission.objects.get_or_create(
                codename=perm_code,
                content_type=order_content_type,
                defaults={'name': perm_code.replace('_', ' ').capitalize()}
            )
            group.permissions.add(perm)

class UauthConfig(AppConfig):
    name = 'core.uauth'

    def ready(self):
        post_migrate.connect(create_user_groups_and_permissions, sender=self)