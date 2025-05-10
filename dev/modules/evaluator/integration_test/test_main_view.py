from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from modules.orders.models import Object, Order, ObjectMeta
from core.uauth.models import UserMeta
from django.contrib.auth.models import Group
from django.utils import timezone

User = get_user_model()

class MainViewIntegrationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.evaluator = User.objects.create_user(
            email='eval@example.com', password='pass', first_name='Eval', last_name='User'
        )
        evaluator_group, _ = Group.objects.get_or_create(name='Evaluator')
        self.evaluator.groups.add(evaluator_group)
        self.client.login(email='eval@example.com', password='pass')
        self.object = Object.objects.create(object_type='Namas', latitude=55.0, longitude=25.0)
        self.order = Order.objects.create(
            client=self.evaluator,
            evaluator=self.evaluator,
            object=self.object,
            status='Naujas'
        )
        UserMeta.objects.create(user=self.evaluator, meta_key='phone_num', meta_value='+37060000000')
        UserMeta.objects.create(user=self.evaluator, meta_key='qualification_certificate_number', meta_value='QC123')
        UserMeta.objects.create(user=self.evaluator, meta_key='date_of_issue_of_certificate', meta_value=str(timezone.now().date()))
        ObjectMeta.objects.create(ev_object=self.object, meta_key='municipality', meta_value='1')

    def test_edit_evaluator_account_get(self):
        url = reverse('modules.evaluator:edit_own_evaluator_account')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertIn('password_form', response.context)

    def test_edit_evaluator_account_post_update_profile(self):
        url = reverse('modules.evaluator:edit_own_evaluator_account')
        data = {
            'first_name': 'EvalUpdated',
            'last_name': 'UserUpdated',
            'email': 'eval@example.com',
            'qualification_certificate_number': 'QC999',
            'date_of_issue_of_certificate': str(timezone.now().date()),
            'phone_num': '+37060000001',
            'update_profile': '1',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.evaluator.refresh_from_db()
        self.assertEqual(self.evaluator.first_name, 'EvalUpdated')

    def test_edit_evaluator_account_post_change_password(self):
        url = reverse('modules.evaluator:edit_own_evaluator_account')
        data = {
            'old_password': 'pass',
            'new_password1': 'newpass123',
            'new_password2': 'newpass123',
            'change_password': '1',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.evaluator.refresh_from_db()
        self.assertTrue(self.evaluator.check_password('newpass123'))

    def test_evaluation_steps_view(self):
        url = reverse('modules.evaluator:evaluation_steps', kwargs={'order_id': self.order.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('order', response.context)
        self.assertEqual(response.context['order'], self.order)

    def test_rc_data_edit_view_get(self):
        url = reverse('modules.evaluator:edit_RC_data', kwargs={'order_id': self.order.id, 'pk': self.object.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('rc_data', response.context)
        self.assertIn('order', response.context)

    def test_rc_data_edit_view_post(self):
        url = reverse('modules.evaluator:edit_RC_data', kwargs={'order_id': self.order.id, 'pk': self.object.id})
        data = {
            'rc_owner': 'Eval Owner',
            'rc_area': '100',
            'rc_cadastral_number': '1234-5678-9012',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)