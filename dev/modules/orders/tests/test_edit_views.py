from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from modules.orders.models import Object, ObjectMeta

User = get_user_model()

class EditAdditionalBuildingsViewTest(TestCase):
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

    def test_get_view_as_regular_user(self):
        url = reverse('modules.orders:edit_additional_buildings', args=[self.object.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('garage_form', response.context)
        self.assertIn('shed_form', response.context)
        self.assertIn('gazebo_form', response.context)

    def test_get_view_as_agency_forbidden(self):
        agency = User.objects.create_user(
            email='agency@example.com',
            password='pass',
            first_name='Agency',
            last_name='User'
        )
        agency.groups.create(name='Agency')
        self.client.logout()
        self.client.login(email='agency@example.com', password='pass')
        url = reverse('modules.orders:edit_additional_buildings', args=[self.object.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Redirect to login or no permission

    def test_post_invalid_data(self):
        url = reverse('modules.orders:edit_additional_buildings', args=[self.object.id])
        response = self.client.post(url, data={'garage_submit': '1'}) 
        self.assertEqual(response.status_code, 200)
        self.assertIn('garage_form', response.context)
        self.assertTrue(response.context['garage_form'].errors)

    def test_post_valid_garage(self):
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
        self.assertTrue(ObjectMeta.objects.filter(ev_object=self.object, meta_key='garage_attached', meta_value='taip').exists())
        self.assertTrue(ObjectMeta.objects.filter(ev_object=self.object, meta_key='garage_cars_count', meta_value='2').exists())