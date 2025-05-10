from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from modules.orders.models import Object, Order, SimilarObject, SimilarObjectMetadata
from core.uauth.models import UserMeta

User = get_user_model()

class SimilarObjectsViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.evaluator = User.objects.create_user(
            email='eval@example.com', password='pass', first_name='Eval', last_name='User'
        )
        self.client.login(email='eval@example.com', password='pass')
        self.object = Object.objects.create(object_type='Namas', latitude=55.0, longitude=25.0)
        from modules.orders.models import ObjectMeta
        ObjectMeta.objects.create(ev_object=self.object, meta_key='municipality', meta_value='1')
        self.order = Order.objects.create(
            client=self.evaluator,
            evaluator=self.evaluator,
            object=self.object,
            status='Naujas'
        )
        self.similar_object = SimilarObject.objects.create(
            original_object=self.object,
            price=100000,
            link='https://example.com',
            description='Test similar object'
        )
        SimilarObjectMetadata.objects.create(
            similar_object=self.similar_object,
            key='living_size',
            value='80'
        )

    def test_similar_object_search_view_get(self):
        url = reverse('modules.evaluator:similar_object_search', args=[self.order.id, self.object.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertIn('order', response.context)
        self.assertIn('object', response.context)

    def test_similar_object_list_view_get(self):
        url = reverse('modules.evaluator:similar_object_list', args=[self.order.id, self.object.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('similar_objects', response.context)
        self.assertEqual(len(response.context['similar_objects']), 1)

    def test_similar_object_list_view_post_delete(self):
        url = reverse('modules.evaluator:similar_object_list', args=[self.order.id, self.object.id])
        response = self.client.post(url, data={'similar_object_id': self.similar_object.id})
        self.assertEqual(response.status_code, 302)
        self.assertFalse(SimilarObject.objects.filter(id=self.similar_object.id).exists())


    def test_edit_similar_object_data_view_get(self):
        url = reverse('modules.evaluator:edit_similar_object_data', args=[self.order.id, self.object.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('similar_object_form', response.context)
        self.assertIn('location_form', response.context)
    
    def test_edit_similar_object_data_view_post_create(self):
        url = reverse('modules.evaluator:edit_similar_object_data', args=[self.order.id, self.object.id])
        data = {
            'price': 123456,
            'link': 'https://test.com',
            'description': 'Test desc',
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
        self.assertTrue(SimilarObject.objects.filter(original_object=self.object, price=123456).exists())

    
    def test_edit_similar_object_decoration_view_get(self):
        url = reverse('modules.evaluator:edit_similar_object_decoration', args=[self.order.id, self.object.id, self.similar_object.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('decoration_form', response.context)
        
    def test_edit_similar_object_common_info_view_get(self):
        url = reverse('modules.evaluator:edit_similar_object_common_info', args=[self.order.id, self.object.id, self.similar_object.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('common_info_form', response.context)
    
    def test_edit_similar_object_utility_info_view_get(self):
        url = reverse('modules.evaluator:edit_similar_object_utility_info', args=[self.order.id, self.object.id, self.similar_object.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('utility_form', response.context)