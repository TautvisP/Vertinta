from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from modules.orders.models import Object, ObjectMeta, Order
from django.contrib.auth.models import Group

User = get_user_model()

class OrderCreationIntegrationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='client@example.com', password='pass', first_name='Client', last_name='User'
        )
        self.client.login(email='client@example.com', password='pass')
        Group.objects.get_or_create(name='User')[0].uauth_user_set.add(self.user)

    def test_order_creation_step_flow(self):
        # Simulate session for object type selection
        session = self.client.session
        session['selected_obj_type'] = 'Namas'
        session.save()
    
        # Step 1: Location and HouseForm
        url = reverse('modules.orders:order_creation_step')
        data = {
            'municipality': '1',  # Use a valid code from MUNICIPALITY_CHOICES
            'street': 'Test gatvė',
            'house_no': 1,
            'latitude': 55.0,
            'longitude': 25.0,
            # HouseForm fields
            'land_purpose': 'Namų valda',  # Use a valid value from LAND_PURPOSE_CHOICES
            'land_size': 10,
            'floor_count': 2,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('modules.orders:order_decoration_step'))
    
        # Step 2: Decoration (fill with valid required fields)
        url = reverse('modules.orders:order_decoration_step')
        data = {
            'outside_deco': 'Tinkuota',  # Example, use valid choices
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
    
    def test_additional_buildings_view_post_garage(self):
        obj = Object.objects.create(object_type='Namas', latitude=55.0, longitude=25.0)
        url = reverse('modules.orders:additional_buildings', args=[obj.id])
        data = {
            'garage-garage_size': 20,
            'garage-garage_attached': 'Taip',
            'garage-garage_cars_count': '2',
            'garage_submit': '1',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('modules.orders:select_agency', args=[obj.id]))
        self.assertTrue(ObjectMeta.objects.filter(ev_object=obj, meta_key='garage_size').exists())