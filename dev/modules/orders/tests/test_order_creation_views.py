from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from modules.orders.models import Object, ObjectMeta, Order

User = get_user_model()

class OrderCreationFlowTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='client@example.com',
            password='pass',
            first_name='Client',
            last_name='User'
        )
        self.client.login(email='client@example.com', password='pass')
        self.object = Object.objects.create(object_type='Namas', latitude=55.0, longitude=25.0)

    def test_order_creation_step_redirects_without_obj_type(self):
        session = self.client.session
        session['selected_obj_type'] = ''
        session.save()
        response = self.client.get(reverse('modules.orders:order_creation_step'))
        self.assertEqual(response.status_code, 302)

    def test_order_creation_step_get(self):
        session = self.client.session
        session['selected_obj_type'] = 'Namas'
        session.save()
        response = self.client.get(reverse('modules.orders:order_creation_step'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('location_form', response.context)
        self.assertIn('additional_form', response.context)

    def test_order_decoration_step_redirects_without_obj_type(self):
        response = self.client.get(reverse('modules.orders:order_decoration_step'))
        self.assertEqual(response.status_code, 302)

    def test_order_decoration_step_get(self):
        session = self.client.session
        session['selected_obj_type'] = 'Namas'
        session['location_data'] = {'latitude': 55.0, 'longitude': 25.0}
        session.save()
        response = self.client.get(reverse('modules.orders:order_decoration_step'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('decoration_form', response.context)

    def test_order_common_info_step_redirects_without_data(self):
        response = self.client.get(reverse('modules.orders:order_common_info_step'))
        self.assertEqual(response.status_code, 302)

    def test_order_utility_step_redirects_without_data(self):
        response = self.client.get(reverse('modules.orders:order_utility_step'))
        self.assertEqual(response.status_code, 302)

    def test_additional_buildings_view_redirects_if_data_exists(self):
        ObjectMeta.objects.create(ev_object=self.object, meta_key='garage_size', meta_value='20')
        Order.objects.create(client=self.user, object=self.object, status='Naujas')
        response = self.client.get(reverse('modules.orders:additional_buildings', args=[self.object.id]))
        self.assertEqual(response.status_code, 400)

    def test_additional_buildings_view_get(self):
        response = self.client.get(reverse('modules.orders:additional_buildings', args=[self.object.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('garage_form', response.context)
        self.assertIn('shed_form', response.context)
        self.assertIn('gazebo_form', response.context)