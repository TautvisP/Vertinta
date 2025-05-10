from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from modules.orders.models import Notification
from django.utils import timezone

User = get_user_model()

class NotificationViewsIntegrationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='user@example.com', password='pass', first_name='Test', last_name='User'
        )
        self.client.login(email='user@example.com', password='pass')
        self.notification1 = Notification.objects.create(
            recipient=self.user,
            title='Test 1',
            message='Message 1',
            created_at=timezone.now(),
            is_read=False,
            notification_type='info',
            action_url='/orders/1/'
        )
        self.notification2 = Notification.objects.create(
            recipient=self.user,
            title='Test 2',
            message='Message 2',
            created_at=timezone.now(),
            is_read=False,
            notification_type='warning',
            action_url='/orders/2/'
        )

    def test_notification_list_view(self):
        url = reverse('modules.orders:notification_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        titles = [n['title'] for n in data]
        self.assertIn('Test 1', titles)
        self.assertIn('Test 2', titles)

    def test_notification_unread_count_view(self):
        url = reverse('modules.orders:notification_unread_count')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 2)

    def test_mark_notification_read_view(self):
        url = reverse('modules.orders:mark_notification_read', args=[self.notification1.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.notification1.refresh_from_db()
        self.assertTrue(self.notification1.is_read)
        self.assertEqual(response.json()['success'], True)

    def test_mark_all_notifications_read_view(self):
        url = reverse('modules.orders:mark_all_notifications_read')
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.notification1.refresh_from_db()
        self.notification2.refresh_from_db()
        self.assertTrue(self.notification1.is_read)
        self.assertTrue(self.notification2.is_read)
        self.assertEqual(response.json()['success'], True)