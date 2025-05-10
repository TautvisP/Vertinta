from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from modules.orders.models import Object, Order, NearbyOrganization, ObjectMeta
from django.contrib.auth.models import Group

User = get_user_model()

class NearbyOrganizationViewTest(TestCase):
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
        self.nearby_org = NearbyOrganization.objects.create(
            object=self.object,
            name='Test School',
            latitude=55.0,
            longitude=25.0,
            address='Test st., Vilnius',
            distance=100,
            category='school'
        )

    def test_found_nearby_organization_view_get(self):
        url = reverse('modules.evaluator:found_organizations', args=[self.order.id, self.object.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('nearby_organizations', response.context)

    def test_nearby_organization_list_view_get(self):
        url = reverse('modules.evaluator:nearby_organization_list', args=[self.order.id, self.object.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('added_nearby_organizations', response.context)

    def test_add_nearby_organization_get(self):
        url = reverse('modules.evaluator:add_nearby_organization', args=[self.order.id, self.object.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)

    def test_add_nearby_organization_post_valid(self):
        url = reverse('modules.evaluator:add_nearby_organization', args=[self.order.id, self.object.id])
        data = {
            'name': 'New School',
            'category': 'school',
            'address': 'New st., Vilnius',
            'distance': 200,
            'latitude': 55.001,
            'longitude': 25.001,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(NearbyOrganization.objects.filter(object=self.object, name='New School').exists())

    def test_add_nearby_organization_post_duplicate(self):
        url = reverse('modules.evaluator:add_nearby_organization', args=[self.order.id, self.object.id])
        data = {
            'name': 'Test School',
            'category': 'school',
            'address': 'Test st., Vilnius',
            'distance': 100,
            'latitude': 55.0,
            'longitude': 25.0,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        # Should not create a duplicate
        self.assertEqual(NearbyOrganization.objects.filter(object=self.object, name='Test School').count(), 1)

    def test_delete_nearby_organization(self):
        url = reverse('modules.evaluator:delete_nearby_organization', args=[self.nearby_org.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(NearbyOrganization.objects.filter(id=self.nearby_org.id).exists())