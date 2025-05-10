from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from modules.orders.models import Object, ObjectMeta, Order
from django.contrib.auth.models import Group

User = get_user_model()

class ObjectDataViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='eval@example.com', password='pass', first_name='Eval', last_name='User'
        )
        evaluator_group, _ = Group.objects.get_or_create(name='Evaluator')
        self.user.groups.add(evaluator_group)
        self.client.login(email='eval@example.com', password='pass')
        self.object = Object.objects.create(object_type='Namas', latitude=55.0, longitude=25.0)
        ObjectMeta.objects.create(ev_object=self.object, meta_key='municipality', meta_value='1')
        self.order = Order.objects.create(
            client=self.user,
            evaluator=self.user,
            object=self.object,
            status='Naujas'
        )

    def test_edit_object_data_view_get(self):
        url = reverse('modules.evaluator:edit_object_data', args=[self.order.id, self.object.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('location_form', response.context)
        self.assertIn('additional_form', response.context)

    def test_edit_object_data_view_post_valid(self):
        url = reverse('modules.evaluator:edit_object_data', args=[self.order.id, self.object.id])
        data = {
            'municipality': '1',
            'street': 'Test st.',
            'house_no': 1,
            'latitude': 55.0,
            'longitude': 25.0,
            'land_purpose': 'Namų valda',
            'land_size': 10,
            'floor_count': 2,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.object.refresh_from_db()
        self.assertEqual(self.object.latitude, 55.0)

    def test_edit_evaluation_and_deco_info_get(self):
        url = reverse('modules.evaluator:edit_evaluation_decoration', args=[self.order.id, self.object.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('decoration_form', response.context)
        self.assertIn('evaluation_form', response.context)

    def test_edit_common_info_get(self):
        url = reverse('modules.evaluator:edit_common_info', args=[self.order.id, self.object.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('common_info_form', response.context)

    def test_edit_utility_info_get(self):
        url = reverse('modules.evaluator:edit_utility_info', args=[self.order.id, self.object.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('utility_form', response.context)

    def test_edit_additional_buildings_get(self):
        url = reverse('modules.evaluator:edit_additional_buildings', args=[self.order.id, self.object.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('garage_form', response.context)
        self.assertIn('shed_form', response.context)
        self.assertIn('gazebo_form', response.context)

    def test_edit_additional_buildings_post_garage(self):
        url = reverse('modules.evaluator:edit_additional_buildings', args=[self.order.id, self.object.id])
        data = {
            'garage-garage_size': 20,
            'garage-garage_attached': 'Taip',
            'garage-garage_cars_count': '2',
            'garage_submit': '1',

        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(ObjectMeta.objects.filter(ev_object=self.object, meta_key='garage_size').exists())

    def test_edit_additional_buildings_post_invalid(self):
        url = reverse('modules.evaluator:edit_additional_buildings', args=[self.order.id, self.object.id])
        data = {
            'garage-garage_type': '',  # Invalid, required field missing
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('garage_form', response.context)