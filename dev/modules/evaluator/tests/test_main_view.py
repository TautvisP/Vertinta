from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from modules.orders.models import Object, Order, ObjectMeta
from core.uauth.models import UserMeta
from django.contrib.auth.models import Group

User = get_user_model()

class MainViewTest(TestCase):
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

    def test_edit_evaluator_account_get(self):
        url = reverse('modules.evaluator:edit_own_evaluator_account')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertIn('password_form', response.context)

    def test_edit_evaluator_account_post_update_profile(self):
        url = reverse('modules.evaluator:edit_own_evaluator_account')
        data = {
            'first_name': 'Eval',
            'last_name': 'User',
            'email': 'eval@example.com',
            'qualification_certificate_number': '12345',
            'date_of_issue_of_certificate': '2020-01-01',
            'phone_num': '+37060000000',
            'update_profile': '1',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Eval')

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
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpass123'))

    def test_evaluation_steps_view_get(self):
        url = reverse('modules.evaluator:evaluation_steps', args=[self.order.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('order', response.context)

    def test_rc_data_edit_view_get(self):
        url = reverse('modules.evaluator:edit_RC_data', kwargs={'order_id': self.order.id, 'pk': self.object.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('rc_data', response.context)
        self.assertIn('order', response.context)
        self.assertIn('object', response.context)

    def test_rc_data_edit_view_post(self):
        url = reverse('modules.evaluator:edit_RC_data', kwargs={'order_id': self.order.id, 'pk': self.object.id})
        data = {
            'rc_field1': 'value1',
            'rc_field2': 'value2',
        }
        response = self.client.post(url, data)
        self.assertIn(response.status_code, [200, 302])