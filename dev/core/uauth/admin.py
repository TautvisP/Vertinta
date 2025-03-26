from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserMeta, AgencyInvitation
from django.urls import reverse_lazy
from django.core.mail import EmailMessage
from django.conf import settings
import traceback
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'date_joined', 'is_staff', 'get_groups')
    search_fields = ('email', 'first_name', 'last_name')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password1', 'password2', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
    )

    def get_groups(self, obj):
        return ", ".join([group.name for group in obj.groups.all()])
    get_groups.short_description = 'Groups'

@admin.register(UserMeta)
class UserMetaAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'meta_key', 'meta_value')
    search_fields = ('user__id', 'meta_key', 'meta_value')
    list_filter = ('meta_key',)

    def user_id(self, obj):
        return obj.user.id
    user_id.short_description = 'User ID'




@admin.register(AgencyInvitation)
class AgencyInvitationAdmin(admin.ModelAdmin):
    list_display = ('email', 'created_at', 'expires_at', 'is_used', 'is_valid')
    search_fields = ('email',)
    list_filter = ('is_used', 'created_at')
    readonly_fields = ('token', 'created_at')
    

    def is_valid(self, obj):
        return not obj.is_used and not obj.is_expired
    
    is_valid.boolean = True
    is_valid.short_description = 'Valid'
    
    actions = ['resend_invitation']
    

    def resend_invitation(self, request, queryset):
        """Resend invitation emails for selected invitations."""

        
        site_url = request.build_absolute_uri('/').rstrip('/')
        success_count = 0
        
        for invitation in queryset:
            if invitation.is_used or invitation.is_expired:
                continue
                
            success = self.send_invitation_email(request, invitation, site_url)

            if success:
                success_count += 1
                
        self.message_user(request, f"{success_count} kvietimai(-ų) išsiųsti(-a) sėkmingai.")
    resend_invitation.short_description = "Išsiųsti pasirinktus kvietimus dar kartą"
    

    def save_model(self, request, obj, form, change):
        """Called when saving an invitation through the admin interface."""

        super().save_model(request, obj, form, change)
        
        if not change:
            site_url = request.build_absolute_uri('/').rstrip('/')
            success = self.send_invitation_email(request, obj, site_url)

            if success:
                self.message_user(request, f"Kvietimas išsiųstas į {obj.email}.", level='SUCCESS')
            else:
                self.message_user(request, f"Nepavyko išsiųsti kvietimo į {obj.email}. Patikrinkite el. pašto nustatymus.", level='ERROR')
    

    def send_invitation_email(self, request, invitation, site_url):
        """Helper method to send invitation email."""

        invitation_url = f"{site_url}{reverse_lazy('core.uauth:agency_register_with_token', kwargs={'token': invitation.token})}"

        print("\n" + "=" * 80)
        print("INVITATION EMAIL WOULD BE SENT")
        print("=" * 80)
        print(f"To: {invitation.email}")
        print(f"Subject: Kvietimas prisijungti prie vertinimo sistemos")
        print("-" * 80)
        print(f"Jūs esate pakviesti prisijungti prie vertinimo sistemos kaip agentūra.")
        print(f"Norėdami užsiregistruoti, spauskite šią nuorodą: {invitation_url}")
        print("=" * 80 + "\n")

        subject = "Kvietimas prisijungti prie vertinimo sistemos"
        message = f"""
    Sveiki,

    Jūs esate pakviesti prisijungti prie nekilnojamojo turto vertinimo sistemos kaip agentūra.

    Norėdami užsiregistruoti, spauskite šią nuorodą: {invitation_url}

    Ši nuoroda galioja 7 dienas nuo išsiuntimo.

    Pagarbiai,
    Vertinimo sistemos administratorius
        """

        # In development environment, just return success after printing to console
        if settings.DEBUG:
            print("Email not sent - running in DEBUG mode. Using console output instead.")
            return True

        # In production, try to send the actual email
        try:
            email = EmailMessage(
                subject=subject,
                body=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[invitation.email],
                headers={'Reply-To': settings.DEFAULT_FROM_EMAIL}
            )

            email.send(fail_silently=False)

            print(f"Email invitation sent successfully to {invitation.email}")
            return True
        except Exception as e:
            print(f"Failed to send email: {str(e)}")
            traceback.print_exc()
            return False