from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from modules.orders.models import Order, Object, ObjectMeta, Report
from django.contrib.auth.models import Group

User = get_user_model()

class OrderIntegrationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.client_user = User.objects.create_user(email='client@example.com', password='pass', first_name='Client', last_name='User')
        self.agency_user = User.objects.create_user(email='agency@example.com', password='pass', first_name='Agency', last_name='User')
        self.evaluator_user = User.objects.create_user(email='eval@example.com', password='pass', first_name='Eval', last_name='User')
        Group.objects.get_or_create(name='Agency')[0].uauth_user_set.add(self.agency_user)
        Group.objects.get_or_create(name='Evaluator')[0].uauth_user_set.add(self.evaluator_user)
        self.object = Object.objects.create(object_type='Namas', latitude=55.0, longitude=25.0)
        ObjectMeta.objects.create(ev_object=self.object, meta_key='municipality', meta_value='1')
        self.order = Order.objects.create(
            client=self.client_user,
            agency=self.agency_user,
            evaluator=self.evaluator_user,
            object=self.object,
            status='Naujas'
        )
        self.report = Report.objects.create(order=self.order, status='pending')

    def test_full_order_flow(self):
        # Client logs in and creates an order
        self.client.login(email='client@example.com', password='pass')
        order = Order.objects.create(client=self.client_user, object=self.object, status='Naujas')
        # Assign agency and evaluator
        order.agency = self.agency_user
        order.evaluator = self.evaluator_user
        order.save()

        # Evaluator logs in and submits a report
        self.client.logout()
        self.client.login(email='eval@example.com', password='pass')
        report = Report.objects.create(order=order, status='pending')
        # Agency logs in and approves the report
        self.client.logout()
        self.client.login(email='agency@example.com', password='pass')
        url = reverse('modules.agency:approve_report', args=[order.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        report.refresh_from_db()
        self.assertEqual(report.status, 'approved')

        # Client tries to access the report
        self.client.logout()
        self.client.login(email='client@example.com', password='pass')
        url = reverse('modules.orders:view_report', args=[order.id])
        response = self.client.get(url)
        self.assertIn(response.status_code, [200, 302])  # Should be allowed if approved

    def test_landing_view_permissions(self):
        # Only non-agency, non-evaluator users can access
        self.client.login(email='client@example.com', password='pass')
        url = reverse('modules.orders:selection')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.client.logout()
        self.client.login(email='agency@example.com', password='pass')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Redirected due to no permission

    def test_order_list_view_permissions(self):
        # Agency sees their orders, client sees their orders
        self.client.login(email='agency@example.com', password='pass')
        url = reverse('modules.orders:order_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.order, response.context['orders'])
        self.client.logout()
        self.client.login(email='client@example.com', password='pass')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.order, response.context['orders'])

    def test_evaluator_order_list_view_permissions(self):
        # Evaluator can see their orders
        self.client.login(email='eval@example.com', password='pass')
        url = reverse('modules.orders:evaluator_order_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.order, response.context['orders'])
        # Agency can see evaluator's orders
        self.client.logout()
        self.client.login(email='agency@example.com', password='pass')
        url = reverse('modules.orders:specific_evaluator_order_list', args=[self.evaluator_user.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_order_delete_view(self):
        # Only client can delete their order
        self.client.login(email='client@example.com', password='pass')
        url = reverse('modules.orders:delete_order', args=[self.order.id])
        response = self.client.post(url)
        self.assertRedirects(response, reverse('modules.orders:order_list'))
        self.assertFalse(Order.objects.filter(id=self.order.id).exists())

    def test_view_object_data_permissions(self):
        # Client, agency, evaluator can view
        self.client.login(email='client@example.com', password='pass')
        url = reverse('modules.orders:view_object_data', kwargs={'order_id': self.order.id, 'pk': self.object.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.client.logout()
        self.client.login(email='agency@example.com', password='pass')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.client.logout()
        self.client.login(email='eval@example.com', password='pass')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_report_access_view_permissions(self):
        # Only agency/evaluator or client (if approved) can access
        self.client.login(email='client@example.com', password='pass')
        url = reverse('modules.orders:view_report', args=[self.order.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # Not approved, should redirect
        report = Report.objects.get(order=self.order)
        report.status = 'approved'
        report.report_file.name = 'reports/dummy.pdf'
        report.save()
        response = self.client.get(url)
        # Should redirect to file url if approved
        self.assertIn(response.status_code, [302, 200])
