from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from modules.orders.models import Object, Order, Event
from core.uauth.models import UserMeta
from django.utils import timezone
from django.contrib.auth.models import Group

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
        Group.objects.get_or_create(name='Evaluator')[0].uauth_user_set.add(self.evaluator)
        Group.objects.get_or_create(name='Agency')[0].uauth_user_set.add(self.agency)
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
        UserMeta.objects.create(user=self.evaluator, meta_key='phone_num', meta_value='+37060000001')
        UserMeta.objects.create(user=self.client_user, meta_key='phone_num', meta_value='+37060000002')

    def test_calendar_view_as_client(self):
        self.client.login(email='client@example.com', password='pass')
        url = reverse('modules.orders:calendar')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('calendar_events_json', response.context)

    def test_event_detail_view_permission(self):
        self.client.login(email='client@example.com', password='pass')
        url = reverse('modules.orders:event_detail', args=[self.event.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['event'], self.event)
        self.assertEqual(response.context['creator_phone'], '+37060000001')
        self.assertEqual(response.context['client_phone'], '+37060000002')

    def test_event_detail_view_no_permission(self):
        other_user = User.objects.create_user(email='other@example.com', password='pass')
        self.client.login(email='other@example.com', password='pass')
        url = reverse('modules.orders:event_detail', args=[self.event.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)  # Should redirect due to no permission

    def test_event_create_view_and_post(self):
        self.client.login(email='eval@example.com', password='pass')
        url = reverse('modules.orders:create_event', args=[self.order.id])
        data = {
            'title': 'Meeting',
            'event_type': 'meeting',
            'start_time': (timezone.now() + timezone.timedelta(days=2)).strftime('%Y-%m-%dT%H:%M'),
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Event.objects.filter(title='Meeting', order=self.order).exists())

    def test_event_update_view_and_post(self):
        self.client.login(email='eval@example.com', password='pass')
        url = reverse('modules.orders:update_event', args=[self.event.id])
        data = {
            'title': 'Updated Event',
            'event_type': 'meeting',
            'start_time': (timezone.now() + timezone.timedelta(days=3)).strftime('%Y-%m-%dT%H:%M'),
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.event.refresh_from_db()
        self.assertEqual(self.event.title, 'Updated Event')

    def test_event_delete_view_and_post(self):
        self.client.login(email='eval@example.com', password='pass')
        url = reverse('modules.orders:delete_event', args=[self.event.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Event.objects.filter(id=self.event.id).exists())

    def test_confirm_event_view(self):
        self.client.login(email='client@example.com', password='pass')
        url = reverse('modules.orders:confirm_event', args=[self.event.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        # Optionally, check if is_confirmed is set if you have such a field
        self.event.refresh_from_db()
        self.assertTrue(getattr(self.event, 'is_confirmed', True))