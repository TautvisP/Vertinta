from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from modules.orders.models import Object, Order, SimilarObject, SimilarObjectMetadata, ObjectMeta
from core.uauth.models import UserMeta
from django.contrib.auth.models import Group


User = get_user_model()

class SimilarObjectsIntegrationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.evaluator = User.objects.create_user(
            email='eval@example.com', password='pass', first_name='Eval', last_name='User'
        )
        Group.objects.get_or_create(name='Evaluator')[0].uauth_user_set.add(self.evaluator)
        self.client.login(email='eval@example.com', password='pass')
        self.client_user = User.objects.create_user(
            email='client@example.com', password='pass', first_name='Client', last_name='User'
        )
        self.object = Object.objects.create(object_type='Namas', latitude=55.0, longitude=25.0)
        self.order = Order.objects.create(client=self.client_user, evaluator=self.evaluator, object=self.object, status='Naujas')
        UserMeta.objects.create(user=self.client_user, meta_key='phone_num', meta_value='+37060000000')
        ObjectMeta.objects.create(ev_object=self.object, meta_key='municipality', meta_value='1')


    def test_create_similar_object(self):
        url = reverse('modules.evaluator:edit_similar_object_data', kwargs={'order_id': self.order.id, 'pk': self.object.id})
        data = {
            'price': 100000,
            'link': 'https://example.com',
            'description': 'Test similar object',
            'municipality': '1',
            'street': 'Test gatvė',
            'house_no': 1,
            'latitude': 55.0,
            'longitude': 25.0,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        similar_object = SimilarObject.objects.filter(original_object=self.object, price=100000).first()

    def test_edit_similar_object(self):
        similar_object = SimilarObject.objects.create(
            original_object=self.object, price=90000, link='https://old.com', description='Old'
        )
        url = reverse('modules.evaluator:edit_similar_object_data', kwargs={'order_id': self.order.id, 'pk': self.object.id})
        data = {
            'edit_id': similar_object.id,
            'price': 120000,
            'link': 'https://new.com',
            'description': 'Updated',
            'municipality': '2',
            'street': 'Updated gatvė',
            'house_no': 2,
            'latitude': 56.0,
            'longitude': 26.0,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        similar_object.refresh_from_db()
        self.assertEqual(similar_object.price, 90000)

    def test_delete_similar_object(self):
        similar_object = SimilarObject.objects.create(
            original_object=self.object, price=50000, link='https://del.com', description='To delete'
        )
        url = reverse('modules.evaluator:similar_object_list', kwargs={'order_id': self.order.id, 'pk': self.object.id})
        response = self.client.post(url, {'similar_object_id': similar_object.id})
        self.assertEqual(response.status_code, 302)
        self.assertFalse(SimilarObject.objects.filter(id=similar_object.id).exists())

    def test_similar_object_list_view(self):
        SimilarObject.objects.create(
            original_object=self.object, price=80000, link='https://list.com', description='List'
        )
        url = reverse('modules.evaluator:similar_object_list', kwargs={'order_id': self.order.id, 'pk': self.object.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('similar_objects', response.context)