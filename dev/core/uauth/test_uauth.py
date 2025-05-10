from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from core.uauth.models import UserMeta, AgencyInvitation
from django.utils import timezone

User = get_user_model()

class UauthViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='user@example.com', password='pass', first_name='Test', last_name='User'
        )
        self.client.login(email='user@example.com', password='pass')

    def test_login_view_get(self):
        self.client.logout()
        url = reverse('core.uauth:login')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'uauth/login.html')

    def test_login_view_post_valid(self):
        self.client.logout()
        url = reverse('core.uauth:login')
        data = {'username': 'user@example.com', 'password': 'pass'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)

    def test_logout_view(self):
        url = reverse('core.uauth:logout')
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

    def test_register_view_get(self):
        self.client.logout()
        url = reverse('core.uauth:register')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'uauth/register.html')

    def test_register_view_post_invalid(self):
        self.client.logout()
        url = reverse('core.uauth:register')
        data = {'email': '', 'password1': '', 'password2': ''}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertIn('email', response.context['form'].errors)

    def test_register_view_post_valid(self):
        self.client.logout()
        url = reverse('core.uauth:register')
        data = {
            'first_name': 'New',
            'last_name': 'User',
            'email': 'newuser@example.com',
            'password1': 'newpass123',
            'password2': 'newpass123'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(email='newuser@example.com').exists())

    def test_agency_register_with_token_get(self):
        self.client.logout()
        invitation = AgencyInvitation.objects.create(
            email='agency@example.com',
            token='12345678-1234-1234-1234-123456789abc',
            is_used=False,
            created_at=timezone.now()
        )
        url = reverse('core.uauth:agency_register_with_token', args=[invitation.token])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'uauth/agency_register.html')

    def test_user_edit_view_get(self):
        url = reverse('core.uauth:edit_profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertIn('password_form', response.context)

    def test_user_edit_view_post_update_profile(self):
        url = reverse('core.uauth:edit_profile')
        data = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'user@example.com',
            'phone_num': '+37060000000',
            'update_profile': '1',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Test')

    def test_user_edit_view_post_change_password(self):
        url = reverse('core.uauth:edit_profile')
        data = {
            'old_password': 'pass',
            'new_password1': 'newpass123',
            'new_password2': 'newpass123',
            'change_password': '1',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpass123'))