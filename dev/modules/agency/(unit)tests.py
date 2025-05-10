from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from modules.orders.models import Order, Report
from core.uauth.models import UserMeta
from django.contrib.auth.models import Group

User = get_user_model()

class AgencyViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.agency = User.objects.create_user(
            email='agency@example.com', password='pass', first_name='Agency', last_name='User'
        )
        agency_group, _ = Group.objects.get_or_create(name='Agency')
        self.agency.groups.add(agency_group)
        self.client.login(email='agency@example.com', password='pass')
        self.evaluator = User.objects.create_user(
            email='eval@example.com', password='pass', first_name='Eval', last_name='User'
        )
        evaluator_group, _ = Group.objects.get_or_create(name='Evaluator')
        self.evaluator.groups.add(evaluator_group)
        self.evaluator.agency = self.agency
        self.evaluator.save()
        self.order = Order.objects.create(
            client=self.agency,
            evaluator=self.evaluator,
            agency=self.agency,
            status='Naujas'
        )
        self.report = Report.objects.create(order=self.order, status='pending')

    def test_edit_agency_account_get(self):
        url = reverse('modules.agency:edit_agency_account')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertIn('password_form', response.context)

    def test_edit_agency_account_post_update_profile(self):
        url = reverse('modules.agency:edit_agency_account')
        data = {
            'agency_name': 'New Agency',
            'main_city': 'Vilnius',
            'phone_num': '+37060000000',
            'email': 'agency@example.com',
            'evaluation_starting_price': '100',
            'update_profile': '1',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)

    def test_edit_agency_account_post_change_password(self):
        url = reverse('modules.agency:edit_agency_account')
        data = {
            'old_password': 'pass',
            'new_password1': 'newpass123',
            'new_password2': 'newpass123',
            'change_password': '1',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.agency.refresh_from_db()
        self.assertTrue(self.agency.check_password('newpass123'))

    def test_evaluator_list_view(self):
        url = reverse('modules.agency:evaluator_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('evaluator_data', response.context)

    def test_create_evaluator_account_get(self):
        url = reverse('modules.agency:create_evaluator_account')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)

    def test_create_evaluator_account_post(self):
        url = reverse('modules.agency:create_evaluator_account')
        data = {
            'first_name': 'Eval2',
            'last_name': 'User2',
            'email': 'eval2@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(email='eval2@example.com').exists())

    def test_approve_report_view(self):
        url = reverse('modules.agency:approve_report', args=[self.order.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.report.refresh_from_db()
        self.assertEqual(self.report.status, 'approved')

    def test_reject_report_view(self):
        url = reverse('modules.agency:reject_report', args=[self.order.id])
        data = {'rejection_reason': 'Incomplete'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.report.refresh_from_db()
        self.assertEqual(self.report.status, 'rejected')
        self.assertEqual(self.report.rejection_reason, 'Incomplete')