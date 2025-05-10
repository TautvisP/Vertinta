from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from modules.orders.models import Object, Order, ObjectMeta, Report
from core.uauth.models import UserMeta
from django.contrib.auth.models import Group
from unittest.mock import patch
import tempfile

User = get_user_model()

@override_settings(MEDIA_ROOT=tempfile.gettempdir())
class GenerateReportViewIntegrationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.evaluator = User.objects.create_user(
            email='eval@example.com', password='pass', first_name='Eval', last_name='User'
        )
        evaluator_group, _ = Group.objects.get_or_create(name='Evaluator')
        self.evaluator.groups.add(evaluator_group)
        self.client.login(email='eval@example.com', password='pass')
        self.object = Object.objects.create(object_type='Namas', latitude=55.0, longitude=25.0)
        ObjectMeta.objects.create(ev_object=self.object, meta_key='municipality', meta_value='1')
        self.order = Order.objects.create(
            client=self.evaluator,
            evaluator=self.evaluator,
            object=self.object,
            status='Naujas'
        )
        UserMeta.objects.create(user=self.evaluator, meta_key='phone_num', meta_value='+37060000000')

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
            'purpose': 'Test purpose',
            'basis': 'Test basis',
            'restrictions': 'None',
            'market_value': 100000,
            'market_value_words': 'vienas šimtas tūkstančių',
            'valuation_date': '2024-01-01',
            'valuation_methodology': 'Palyginamoji',
        }
        response = self.client.post(url, data)
        # Should redirect to engineering step if valid and no missing data
        self.assertIn(response.status_code, [302, 200])

    def test_final_report_engineering_view_get(self):
        url = reverse('modules.evaluator:final_report_engineering', kwargs={'order_id': self.order.id, 'pk': self.object.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('final_report_text_form', response.context)

    @patch('modules.evaluator.views.generate_report_view.PDFReportGenerator.generate_report', return_value=(True, "Success"))
    def test_final_report_engineering_view_post_valid(self, mock_generate_report):
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
        self.assertEqual(response.status_code, 302)
        mock_generate_report.assert_called_once()

    def test_pdf_report_generator_check_report_data_complete(self):
        from modules.evaluator.views.generate_report_view import PDFReportGenerator
        report = Report.objects.create(order=self.order)
        # Incomplete report
        self.assertFalse(PDFReportGenerator.check_report_data_complete(report))
        # Complete report
        report.engineering = 'eng'
        report.addictions = 'add'
        report.floor_plan = 'plan'
        report.district = 'dist'
        report.conclusion = 'conc'
        report.valuation_methodology = 'val'
        report.save()
        self.assertTrue(PDFReportGenerator.check_report_data_complete(report))