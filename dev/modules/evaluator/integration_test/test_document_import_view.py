from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from modules.orders.models import Object, Order, UploadedDocument, ObjectMeta
from core.uauth.models import UserMeta
from django.contrib.auth.models import Group
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch
import tempfile
import os

User = get_user_model()

@override_settings(MEDIA_ROOT=tempfile.gettempdir())
class DocumentImportViewIntegrationTest(TestCase):
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

    def test_document_import_view_get(self):
        url = reverse('modules.evaluator:document_import', kwargs={'order_id': self.order.id, 'pk': self.object.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertIn('uploaded_documents', response.context)

    @patch('modules.evaluator.views.document_import_view.DocumentImportView.convert_to_pdf')
    def test_document_import_view_post_txt(self, mock_convert_to_pdf):
        url = reverse('modules.evaluator:document_import', kwargs={'order_id': self.order.id, 'pk': self.object.id})
        mock_convert_to_pdf.return_value = SimpleUploadedFile('test.pdf', b'%PDF-1.4 content', content_type='application/pdf')
        txt_file = SimpleUploadedFile('test.txt', b'Hello\nWorld', content_type='text/plain')
        data = {'file': txt_file, 'comment': 'Test comment'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(UploadedDocument.objects.filter(order=self.order, file_name='test.pdf').exists())

    @patch('modules.evaluator.views.document_import_view.DocumentImportView.convert_to_pdf')
    def test_document_import_view_post_docx(self, mock_convert_to_pdf):
        url = reverse('modules.evaluator:document_import', kwargs={'order_id': self.order.id, 'pk': self.object.id})
        mock_convert_to_pdf.return_value = SimpleUploadedFile('test.pdf', b'%PDF-1.4 content', content_type='application/pdf')
        docx_file = SimpleUploadedFile('test.docx', b'docxcontent', content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        data = {'file': docx_file, 'comment': 'Test comment'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(UploadedDocument.objects.filter(order=self.order, file_name='test.pdf').exists())

    @patch('modules.evaluator.views.document_import_view.DocumentImportView.convert_to_pdf')
    def test_document_import_view_post_odt(self, mock_convert_to_pdf):
        url = reverse('modules.evaluator:document_import', kwargs={'order_id': self.order.id, 'pk': self.object.id})
        mock_convert_to_pdf.return_value = SimpleUploadedFile('test.pdf', b'%PDF-1.4 content', content_type='application/pdf')
        odt_file = SimpleUploadedFile('test.odt', b'odtcontent', content_type='application/vnd.oasis.opendocument.text')
        data = {'file': odt_file, 'comment': 'Test comment'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(UploadedDocument.objects.filter(order=self.order, file_name='test.pdf').exists())

    def test_document_view_get(self):
        doc = UploadedDocument.objects.create(
            order=self.order,
            file_name='test.pdf',
            file_path=SimpleUploadedFile('test.pdf', b'%PDF-1.4 content', content_type='application/pdf'),
            comment='Test'
        )
        url = reverse('modules.evaluator:view_document', kwargs={'document_id': doc.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')

    def test_delete_document_view_post(self):
        doc = UploadedDocument.objects.create(
            order=self.order,
            file_name='test.pdf',
            file_path=SimpleUploadedFile('test.pdf', b'%PDF-1.4 content', content_type='application/pdf'),
            comment='Test'
        )
        url = reverse('modules.evaluator:delete_document', kwargs={'document_id': doc.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 400)
        self.assertFalse(UploadedDocument.objects.filter(id=doc.id).exists())

    def test_update_document_comment_view_post(self):
        doc = UploadedDocument.objects.create(
            order=self.order,
            file_name='test.pdf',
            file_path=SimpleUploadedFile('test.pdf', b'%PDF-1.4 content', content_type='application/pdf'),
            comment='Old comment'
        )
        url = reverse('modules.evaluator:update_document_comment')
        data = {'document_id': doc.id, 'comment': 'New comment'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        doc.refresh_from_db()
        self.assertEqual(doc.comment, 'New comment')
        self.assertEqual(response.json()['status'], 'success')