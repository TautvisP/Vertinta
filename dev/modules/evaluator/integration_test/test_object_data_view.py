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
        url = reverse('modules.evaluator:edit_object_data', kwargs={'order_id': self.order.id, 'pk': self.object.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('location_form', response.context)
        self.assertIn('additional_form', response.context)

    def test_edit_object_data_view_post(self):
        url = reverse('modules.evaluator:edit_object_data', kwargs={'order_id': self.order.id, 'pk': self.object.id})
        data = {
            'municipality': '1',
            'street': 'Test gatvė',
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
        self.assertTrue(ObjectMeta.objects.filter(ev_object=self.object, meta_key='land_purpose', meta_value='Namų valda').exists())

    def test_edit_evaluation_and_deco_info_get(self):
        url = reverse('modules.evaluator:edit_evaluation_decoration', kwargs={'order_id': self.order.id, 'pk': self.object.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('decoration_form', response.context)
        self.assertIn('evaluation_form', response.context)

    def test_edit_evaluation_and_deco_info_post(self):
        url = reverse('modules.evaluator:edit_evaluation_decoration', kwargs={'order_id': self.order.id, 'pk': self.object.id})
        data = {
            'outside_deco': 'Tinkuota',
            'interior_deco': 'Dažyta',
            'interior_floors': 'Parketas',
            'ceiling_deco': 'Dažyta',
            'windows': 'Plastikiniai',
            'inside_doors': 'Medinės',
            'outside_doors': 'Šarvuotos',
            'parking_spaces': 1,
            'basement': 'Yra',
            'balcony': 'Yra',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)

    def test_edit_common_info_get(self):
        url = reverse('modules.evaluator:edit_common_info', kwargs={'order_id': self.order.id, 'pk': self.object.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('common_info_form', response.context)

    def test_edit_common_info_post(self):
        url = reverse('modules.evaluator:edit_common_info', kwargs={'order_id': self.order.id, 'pk': self.object.id})
        data = {
            'room_count': 3,
            'living_size': 80,
            'build_years': 2000,
            'renovation_years': 2015,
            'foundation': 'Betonas',
            'walls': 'Mūrinės',
            'inside_walls': 'Gipsas',
            'subfloor': 'Betonas',
            'roof': 'Skarda',
            'municipality': '1',
            'street': 'Test gatvė',
            'house_no': 1,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)

    def test_edit_utility_info_get(self):
        url = reverse('modules.evaluator:edit_utility_info', kwargs={'order_id': self.order.id, 'pk': self.object.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('utility_form', response.context)

    def test_edit_utility_info_post(self):
        url = reverse('modules.evaluator:edit_utility_info', kwargs={'order_id': self.order.id, 'pk': self.object.id})
        data = {
            'electricity': 'Yra',
            'gas': 'Yra',
            'heating': 'Centrinis',
            'water': 'Miesto',
            'wastewater': 'Miesto',
            'air_conditioning': 'Nėra',
            'security': 'Nėra',
            'energy_efficiency': 'B',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)

    def test_edit_additional_buildings_get(self):
        url = reverse('modules.evaluator:edit_additional_buildings', kwargs={'order_id': self.order.id, 'pk': self.object.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('garage_form', response.context)
        self.assertIn('shed_form', response.context)
        self.assertIn('gazebo_form', response.context)

    def test_edit_additional_buildings_post_garage(self):
        url = reverse('modules.evaluator:edit_additional_buildings', kwargs={'order_id': self.order.id, 'pk': self.object.id})
        data = {
            'garage-garage_size': 20,
            'garage-garage_attached': 'Taip',
            'garage-garage_cars_count': '2',
            'garage_submit': '1',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(ObjectMeta.objects.filter(ev_object=self.object, meta_key='garage_size').exists())