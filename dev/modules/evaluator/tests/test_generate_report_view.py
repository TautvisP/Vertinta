from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from modules.orders.models import Object, Order, ObjectMeta, Report, UploadedDocument, NearbyOrganization, ObjectImage, SimilarObject
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import Group

User = get_user_model()

class GenerateReportViewTest(TestCase):
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
        ObjectMeta.objects.create(ev_object=self.object, meta_key='street', meta_value='Test st.')
        ObjectMeta.objects.create(ev_object=self.object, meta_key='house_no', meta_value='1')
        self.order = Order.objects.create(
            client=self.user,
            evaluator=self.user,
            object=self.object,
            status='Naujas'
        )
        self.report = Report.objects.create(order=self.order)
        ObjectMeta.objects.create(ev_object=self.object, meta_key='garage_size', meta_value='20')
        ObjectImage.objects.create(object=self.object, image=SimpleUploadedFile("test.jpg", b"filecontent", content_type="image/jpeg"))
        SimilarObject.objects.create(original_object=self.object, price=100000, link='https://test.com', description='desc')
        UploadedDocument.objects.create(
            order=self.order,
            file_name="doc.pdf",
            content="filecontent"
        )
        NearbyOrganization.objects.create(object=self.object, name='School', latitude=55.0, longitude=25.0, address='Test', distance=100, category='school')

    def test_generate_report_view_get(self):
        url = reverse('modules.evaluator:generate_report', kwargs={'order_id': self.order.id, 'pk': self.object.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('final_report_form', response.context)
        self.assertIn('missing_data', response.context)

    def test_generate_report_view_post_invalid(self):
        url = reverse('modules.evaluator:generate_report', kwargs={'order_id': self.order.id, 'pk': self.object.id})
        # Missing required fields for FinalReportForm
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, 200)
        self.assertIn('final_report_form', response.context)
        self.assertTrue(response.context['final_report_form'].errors)

    def test_generate_report_view_post_valid(self):
        url = reverse('modules.evaluator:generate_report', kwargs={'order_id': self.order.id, 'pk': self.object.id})
        data = {
            'visit_date': '2024-01-01',
            'report_date': '2024-01-02',
            'description': 'Test description',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)

    def test_final_report_engineering_view_get(self):
        url = reverse('modules.evaluator:final_report_engineering', kwargs={'order_id': self.order.id, 'pk': self.object.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('final_report_text_form', response.context)

    def test_final_report_engineering_view_post_invalid(self):
        url = reverse('modules.evaluator:final_report_engineering', kwargs={'order_id': self.order.id, 'pk': self.object.id})
        # Missing required fields for FinalReportEngineeringForm
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, 200)
        self.assertIn('final_report_text_form', response.context)
        self.assertTrue(response.context['final_report_text_form'].errors)

    def test_final_report_engineering_view_post_valid(self):
        url = reverse('modules.evaluator:final_report_engineering', kwargs={'order_id': self.order.id, 'pk': self.object.id})
        data = {
            'engineering': 'Test engineering',
            'addictions': 'None',
            'floor_plan': 'Plan',
            'district': 'District',
            'conclusion': 'Conclusion',
            'valuation_methodology': 'Palyginamoji',
        }
        response = self.client.post(url, data)
        self.assertIn(response.status_code, [200, 302])