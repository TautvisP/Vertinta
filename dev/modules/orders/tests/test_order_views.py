from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from modules.orders.models import Order, Object, ObjectMeta
from core.uauth.models import UserMeta
from django.utils import timezone

User = get_user_model()

class OrderViewsTest(TestCase):
    def setUp(self):
            self.client = Client()
            self.user = User.objects.create_user(
                email='client@example.com',
                password='pass',
                first_name='Client',
                last_name='User'
            )
            self.agency = User.objects.create_user(
                email='agency@example.com',
                password='pass',
                first_name='Agency',
                last_name='User'
            )
            agency_group, _ = self.agency.groups.get_or_create(name='Agency')
            self.agency.groups.add(agency_group)
            self.object = Object.objects.create(object_type='Butas')
            ObjectMeta.objects.create(ev_object=self.object, meta_key='municipality', meta_value='1')
            self.order = Order.objects.create(
                client=self.user,
                object=self.object,
                agency=self.agency,
                status='Naujas',
                priority='Vidutinis'
            )
            self.client.login(email='client@example.com', password='pass')


    def test_order_list_view(self):
        response = self.client.get(reverse('modules.orders:order_list'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('orders', response.context)

    def test_order_delete_view(self):
        response = self.client.post(reverse('modules.orders:delete_order', args=[self.order.id]))
        self.assertEqual(response.status_code, 302)  # Redirect after delete

    def test_view_object_data_view(self):
        response = self.client.get(reverse('modules.orders:view_object_data', args=[self.order.id, self.object.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('meta_data', response.context)

    def test_report_access_view_denied(self):
        # Report not approved, should redirect
        response = self.client.get(reverse('modules.orders:view_report', args=[self.order.id]))
        self.assertEqual(response.status_code, 302)

    def test_landing_view(self):
        self.client.logout()
        response = self.client.get(reverse('modules.orders:selection'))
        self.assertEqual(response.status_code, 302)  # Should redirect to login

    def test_agency_selection_view(self):
        self.client.logout()
        self.client.login(email='client@example.com', password='pass')
        response = self.client.get(reverse('modules.orders:select_agency_object', args=[self.object.id]))
        self.assertEqual(response.status_code, 200)