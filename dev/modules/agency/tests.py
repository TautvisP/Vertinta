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
        self.client_user = User.objects.create_user(
            email='client@example.com', password='pass', first_name='Client', last_name='User'
        )
        self.order = Order.objects.create(
            client=self.client_user,
            evaluator=self.evaluator,
            agency=self.agency,
            status='Naujas'
        )
        self.report = Report.objects.create(order=self.order, status='pending')

    def test_approve_report_view(self):
        url = reverse('modules.agency:approve_report', args=[self.order.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.report.refresh_from_db()
        self.assertEqual(self.report.status, 'approved')

    def test_approve_report_view_wrong_agency(self):
        other_agency = User.objects.create_user(
            email='otheragency@example.com', password='pass', first_name='Other', last_name='Agency'
        )
        Group.objects.get_or_create(name='Agency')[0].uauth_user_set.add(other_agency)
        self.client.logout()
        self.client.login(email='otheragency@example.com', password='pass')
        url = reverse('modules.agency:approve_report', args=[self.order.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.report.refresh_from_db()
        self.assertNotEqual(self.report.status, 'approved')

    def test_approve_report_view_no_report(self):
        self.report.delete()
        url = reverse('modules.agency:approve_report', args=[self.order.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

    def test_reject_report_view(self):
        url = reverse('modules.agency:reject_report', args=[self.order.id])
        data = {'rejection_reason': 'Test rejection'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.report.refresh_from_db()
        self.assertEqual(self.report.status, 'rejected')
        self.assertEqual(self.report.rejection_reason, 'Test rejection')

    def test_reject_report_view_no_reason(self):
        url = reverse('modules.agency:reject_report', args=[self.order.id])
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, 302)
        self.report.refresh_from_db()
        self.assertNotEqual(self.report.status, 'rejected')

    def test_reject_report_view_wrong_agency(self):
        other_agency = User.objects.create_user(
            email='otheragency@example.com', password='pass', first_name='Other', last_name='Agency'
        )
        Group.objects.get_or_create(name='Agency')[0].uauth_user_set.add(other_agency)
        self.client.logout()
        self.client.login(email='otheragency@example.com', password='pass')
        url = reverse('modules.agency:reject_report', args=[self.order.id])
        data = {'rejection_reason': 'Test rejection'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.report.refresh_from_db()
        self.assertNotEqual(self.report.status, 'rejected')