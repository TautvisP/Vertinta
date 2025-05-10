from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from modules.orders.models import Notification

User = get_user_model()

class NotificationViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='pass',
            first_name='Test',
            last_name='User'
        )
        self.client.login(email='test@example.com', password='pass')
        self.notification = Notification.objects.create(
            recipient=self.user,
            title='Test',
            message='Test message',
            notification_type='info',
            action_url='/',
            is_read=False
        )

    def test_notification_list_view(self):
        url = reverse('modules.orders:notification_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response.json(), list))
        self.assertEqual(response.json()[0]['title'], 'Test')

    def test_notification_unread_count_view(self):
        url = reverse('modules.orders:notification_unread_count')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 1)

    def test_mark_notification_read_view(self):
        url = reverse('modules.orders:mark_notification_read', args=[self.notification.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.notification.refresh_from_db()
        self.assertTrue(self.notification.is_read)
        self.assertTrue(response.json()['success'])

    def test_mark_all_notifications_read_view(self):
        url = reverse('modules.orders:mark_all_notifications_read')
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.notification.refresh_from_db()
        self.assertTrue(self.notification.is_read)
        self.assertTrue(response.json()['success'])