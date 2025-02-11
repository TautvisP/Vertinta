from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, Group
from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.core.exceptions import MultipleObjectsReturned
from django.utils.translation import gettext as _
from modules.orders.enums import STATUS_CHOICES

USER_GROUPS = [
    'Client',
    'Appraiser',
    'Agency',
    'Admin',
]

class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):

        if not email:
            raise ValueError(_('Nenustatytas el. pašto adresas'))
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField(verbose_name="email address", unique=True, error_messages={
        'required': _('Šis laukas yra privalomas')
    })
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    agency = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='evaluators')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'


    #class Meta:
    #    permissions = [('can_login_as_agency', 'Can login as agency'),
    #                   ('can_login_as_appr', 'Can login as appraiser'),
    #                   ('can_login_as_client', 'Can login as client'),
    #                   ('can_delete_order_details', 'Can delete order details'),
    #                   ('can_delete_evaluation', 'can_delete_evaluation'),
    #                   ('redirect_to_cilent_order_list',
    #                    'Should be redirected to client order list'),
    #                   ('has_view_order_button',
    #                    'Has view order button in order list'),
    #                   ('can_evaluate', 'Can make evaluation'),
    #                   ('can_edit_ev_details', 'Can edit order'),
    #                   ('can_view_notifications', 'Can view notification'),
    #                   ('can_change_appraiser', 'Can change evaluation request appr'),
    #                   ('can_change_order_priority', 'Can change order priority'),
    #                   ('can_view_report', 'Can download report'),
    #                   ('redirect_to_agency_order_list',
    #                    'Should be redirected to agency order list'),
    #                   ]

    groups = models.ManyToManyField(
        Group,
        verbose_name="groups",
        blank=True,
        help_text=(
            "The groups this user belongs to. A user will get all permissions granted to each of their groups."
        ),
        related_name="uauth_user_set",
        related_query_name="uauth_user",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name="user permissions",
        blank=True,
        help_text="Specific permissions for this user.",
        related_name="uauth_user_set",
        related_query_name="uauth_user",
    )

    @classmethod
    def get_meta(self, user, key):

        try:
            return UserMeta.objects.values_list('meta_value', flat=True).get(user=user, meta_key=key)
        
        except (MultipleObjectsReturned, UserMeta.DoesNotExist):
            return ''

    def save_meta(self, key, value):
        object_meta, created = UserMeta.objects.get_or_create(
            user=self, meta_key=key)
        object_meta.meta_value = value
        object_meta.save()

    @classmethod
    def save_user(cls, user):
        user.is_active = False
        user.save()

    def update_profile(self, form, meta_keys):
        if not form.is_valid():
            return

        for key in meta_keys:
            if form.cleaned_data[key] is not None:
                self.save_meta(key, form.cleaned_data[key])

    #@classmethod
    #def save_user_group_with_perm(cls, user, group_name, permission_name):
    #    group = Group.objects.get(name=group_name)
    #    user.groups.add(group)
    #    for perm in permission_name:
    #        permission = Permission.objects.get(
    #            codename=perm)
    #        user.user_permissions.add(permission)

    #@classmethod
    #def send_password_create_email(cls, user, token_generator, request, url, form):
    #    activation_page = render_to_string('registration/create_password_mail.html', {
    #        'user': user,
    #        'uid': str(urlsafe_base64_encode(force_bytes(user.pk))),
    #        'domain': get_current_site(request).domain,
    #        'token': token_generator.make_token(user)
    #    })
    #    try:
    #        email_message = EmailMessage(
    #            'Activate account', activation_page, to=[user.email])
    #        email_message.send()
    #    except (Exception, SMTPException):
    #        form.errors[NON_FIELD_ERRORS] = form.error_class(
    #            [_('Negalime išsiųsti laiško į nurodytą adresą.')])
    #        return render(request, url, {'form': form})

    @property
    def ongoing_orders_count(self):
        return self.evaluator_orders.filter(status=STATUS_CHOICES[3][0]).count()

    @property
    def completed_orders_count(self):
        return self.evaluator_orders.filter(status=STATUS_CHOICES[4][0]).count()

class UserMeta(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    meta_key = models.CharField(max_length=255)
    meta_value = models.CharField(max_length=255)

    @classmethod
    def get_meta(cls, user, key):
        try:
            return cls.objects.values_list('meta_value', flat=True).get(user=user, meta_key=key)
        
        except (cls.DoesNotExist, MultipleObjectsReturned):
            return ''