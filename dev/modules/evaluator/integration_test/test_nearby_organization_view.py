from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from modules.orders.models import Object, Order, NearbyOrganization, ObjectMeta
from django.contrib.auth.models import Group
from unittest.mock import patch

User = get_user_model()

class NearbyOrganizationIntegrationTest(TestCase):
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

    def test_found_nearby_organization_view_get(self):
        url = reverse('modules.evaluator:found_organizations', kwargs={'order_id': self.order.id, 'pk': self.object.id})
        with patch('modules.evaluator.views.nearby_organization_view.FoundNearbyOrganizationView.find_nearby_organizations', return_value=[
            {'name': 'Test School', 'latitude': 55.0, 'longitude': 25.0, 'address': 'Test St, City', 'distance': 100, 'category': 'school'}
        ]):
            response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('nearby_organizations', response.context)
        self.assertEqual(response.context['nearby_organizations'][0]['name'], 'Test School')

    def test_found_nearby_organization_view_post(self):
        url = reverse('modules.evaluator:found_organizations', kwargs={'order_id': self.order.id, 'pk': self.object.id})
        data = {
            'name': 'Test Org',
            'latitude': '55.000000',
            'longitude': '25.000000',
            'address': 'Test Address',
            'distance': '123',
            'category': 'school'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(NearbyOrganization.objects.filter(object=self.object, name='Test Org').exists())

    def test_nearby_organization_list_view(self):
        NearbyOrganization.objects.create(
            object=self.object,
            name='Test Org',
            latitude=55.0,
            longitude=25.0,
            address='Test Address',
            distance=123,
            category='school'
        )
        url = reverse('modules.evaluator:nearby_organization_list', kwargs={'order_id': self.order.id, 'pk': self.object.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('added_nearby_organizations', response.context)
        self.assertEqual(response.context['added_nearby_organizations'][0].name, 'Test Org')

    def test_add_nearby_organization_view_get(self):
        url = reverse('modules.evaluator:add_nearby_organization', kwargs={'order_id': self.order.id, 'pk': self.object.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)

    def test_add_nearby_organization_view_post(self):
        url = reverse('modules.evaluator:add_nearby_organization', kwargs={'order_id': self.order.id, 'pk': self.object.id})
        data = {
            'name': 'Another Org',
            'latitude': 55.0,
            'longitude': 25.0,
            'address': 'Another Address',
            'distance': 321,
            'category': 'hospital'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(NearbyOrganization.objects.filter(object=self.object, name='Another Org').exists())

    def test_delete_nearby_organization_view(self):
        org = NearbyOrganization.objects.create(
            object=self.object,
            name='Delete Org',
            latitude=55.0,
            longitude=25.0,
            address='Del Address',
            distance=222,
            category='pharmacy'
        )
        url = reverse('modules.evaluator:delete_nearby_organization', kwargs={'organization_id': org.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(NearbyOrganization.objects.filter(id=org.id).exists())