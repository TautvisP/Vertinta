from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from modules.orders.models import Object, ObjectMeta, Order
from django.contrib.auth.models import Group

User = get_user_model()

class EditObjectStepIntegrationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='client@example.com', password='pass', first_name='Client', last_name='User'
        )
        self.client.login(email='client@example.com', password='pass')
        Group.objects.get_or_create(name='User')[0].uauth_user_set.add(self.user)
        self.object = Object.objects.create(object_type='Namas', latitude=55.0, longitude=25.0)
        ObjectMeta.objects.create(ev_object=self.object, meta_key='municipality', meta_value='1')
        self.order = Order.objects.create(client=self.user, object=self.object, status='Naujas')

    def test_edit_object_step_post(self):
        url = reverse('modules.orders:edit_object_step', kwargs={'pk': self.object.id})
        data = {
            # ObjectLocationForm
            'municipality': '1',
            'street': 'Test gatvė',
            'house_no': 1,
            'latitude': 55.0,
            'longitude': 25.0,
            # HouseForm
            'land_purpose': 'Namų valda',
            'land_size': 10,
            'floor_count': 2,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.object.refresh_from_db()
        self.assertEqual(self.object.latitude, 55.0)
        self.assertTrue(ObjectMeta.objects.filter(ev_object=self.object, meta_key='land_purpose', meta_value='Namų valda').exists())

    # def test_edit_object_decoration_step_post(self):
    #     url = reverse('modules.orders:edit_decoration_step', kwargs={'pk': self.object.id})
    #     data = {
    #         'outside_deco': 'Tinkuota',
    #         'interior_deco': 'Dažyta',
    #         'interior_floors': 'Parketas',
    #         'ceiling_deco': 'Dažyta',
    #         'windows': 'Plastikiniai',
    #         'inside_doors': 'Medinės',
    #         'outside_doors': 'Šarvuotos',
    #         'parking_spaces': 1,
    #         'basement': 'Yra',
    #         'balcony': 'Yra',
    #     }
    #     response = self.client.post(url, data)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTrue(ObjectMeta.objects.filter(ev_object=self.object, meta_key='outside_deco', meta_value='Tinkuota').exists())

    # def test_edit_object_common_info_step_post(self):
    #     url = reverse('modules.orders:edit_common_info_step', kwargs={'pk': self.object.id})
    #     data = {
    #         'room_count': 3,
    #         'living_size': 80,
    #         'build_years': 2000,
    #         'renovation_years': 2015,
    #         'foundation': 'Betonas',
    #         'walls': 'Mūrinės',
    #         'inside_walls': 'Gipsas',
    #         'subfloor': 'Betonas',
    #         'roof': 'Skarda',
    #         'municipality': '1',
    #         'street': 'Test gatvė',
    #         'house_no': 1,
    #     }
    #     response = self.client.post(url, data)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTrue(ObjectMeta.objects.filter(ev_object=self.object, meta_key='foundation', meta_value='Betonas').exists())

    # def test_edit_object_utility_step_post(self):
    #     url = reverse('modules.orders:edit_utility_step', kwargs={'pk': self.object.id})
    #     data = {
    #         'electricity': 'Yra',
    #         'gas': 'Yra',
    #         'heating': 'Centrinis',
    #         'water': 'Miesto',
    #         'wastewater': 'Miesto',
    #         'air_conditioning': 'Nėra',
    #         'security': 'Nėra',
    #         'energy_efficiency': 'B',
    #     }
    #     response = self.client.post(url, data)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertTrue(ObjectMeta.objects.filter(ev_object=self.object, meta_key='electricity', meta_value='Yra').exists())

    def test_edit_additional_buildings_post_garage(self):
        url = reverse('modules.orders:edit_additional_buildings', args=[self.object.id])
        data = {
            'garage_submit': '1',
            'garage-garage_size': '20',
            'garage-garage_attached': 'Taip',
            'garage-garage_cars_count': '2',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(ObjectMeta.objects.filter(ev_object=self.object, meta_key='garage_size', meta_value='20').exists())
        self.assertTrue(ObjectMeta.objects.filter(ev_object=self.object, meta_key='garage_attached', meta_value='Taip').exists())
        self.assertTrue(ObjectMeta.objects.filter(ev_object=self.object, meta_key='garage_cars_count', meta_value='2').exists())