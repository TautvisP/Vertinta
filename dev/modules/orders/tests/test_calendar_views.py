from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from modules.orders.models import Order, Event, Object
from core.uauth.models import UserMeta

User = get_user_model()

class CalendarViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.client_user = User.objects.create_user(
            email='client@example.com', password='pass', first_name='Client', last_name='User'
        )
        self.evaluator = User.objects.create_user(
            email='eval@example.com', password='pass', first_name='Eval', last_name='User'
        )
        self.agency = User.objects.create_user(
            email='agency@example.com', password='pass', first_name='Agency', last_name='User'
        )
        self.object = Object.objects.create(object_type='Namas', latitude=55.0, longitude=25.0)
        self.order = Order.objects.create(
            client=self.client_user,
            evaluator=self.evaluator,
            agency=self.agency,
            object=self.object,
            status='Naujas'
        )
        self.event = Event.objects.create(
            order=self.order,
            title='Test Event',
            event_type='meeting',
            start_time=timezone.now() + timezone.timedelta(days=1),
            created_by=self.evaluator
        )
        self.event = Event.objects.create(
            order=self.order,
            title='Test Event',
            event_type='meeting',
            start_time=timezone.now() + timezone.timedelta(days=1),
            created_by=self.evaluator
        )
    def test_calendar_view_as_client(self):
        self.client.login(email='client@example.com', password='pass')
        url = reverse('modules.orders:calendar')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('calendar_events_json', response.context)

    def test_event_detail_permissions(self):
        self.client.login(email='client@example.com', password='pass')
        url = reverse('modules.orders:event_detail', args=[self.event.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.client.login(email='eval@example.com', password='pass')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.client.login(email='agency@example.com', password='pass')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_confirm_event_view(self):
        self.client.login(email='client@example.com', password='pass')
        url = reverse('modules.orders:confirm_event', args=[self.event.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.event.refresh_from_db()
        self.assertTrue(self.event.is_confirmed)

    def test_confirm_event_permission_denied(self):
        self.client.login(email='eval@example.com', password='pass')
        url = reverse('modules.orders:confirm_event', args=[self.event.id])
        response = self.client.post(url)
        self.assertNotEqual(response.status_code, 302)  # Should not redirect (permission denied)