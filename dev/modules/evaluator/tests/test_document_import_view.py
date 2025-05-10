from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from modules.orders.models import Object, Order, UploadedDocument, ObjectMeta
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import Group
from django.conf import settings
import os

User = get_user_model()

class DocumentImportViewTest(TestCase):
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

    def test_document_import_view_get(self):
        url = reverse('modules.evaluator:document_import', kwargs={'order_id': self.order.id, 'pk': self.object.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertIn('uploaded_documents', response.context)

    def test_document_import_view_post_txt(self):
        url = reverse('modules.evaluator:document_import', kwargs={'order_id': self.order.id, 'pk': self.object.id})
        txt_file = SimpleUploadedFile("test.txt", b"Hello\nWorld", content_type="text/plain")
        data = {
            'file': txt_file,
            'comment': 'Test comment'
        }
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(UploadedDocument.objects.filter(order=self.order, file_name__endswith='.pdf').exists())

    def test_document_import_view_post_invalid(self):
        url = reverse('modules.evaluator:document_import', kwargs={'order_id': self.order.id, 'pk': self.object.id})
        data = {'comment': 'No file'}
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertFalse(response.context['form'].is_valid())

    def test_delete_document_view(self):
        doc = UploadedDocument.objects.create(
            order=self.order,
            file_name="test.pdf",
            file_path="uploaded_documents/test.pdf",
            comment="to be deleted"
        )
        url = reverse('modules.evaluator:delete_document', args=[doc.id])
        response = self.client.post(url, HTTP_REFERER=reverse('modules.evaluator:document_import', kwargs={'order_id': self.order.id, 'pk': self.object.id}))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(UploadedDocument.objects.filter(id=doc.id).exists())

    def test_update_document_comment_view(self):
        doc = UploadedDocument.objects.create(
            order=self.order,
            file_name="test.pdf",
            file_path="uploaded_documents/test.pdf",
            comment="old comment"
        )
        url = reverse('modules.evaluator:update_document_comment')
        data = {'document_id': doc.id, 'comment': 'new comment'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        doc.refresh_from_db()
        self.assertEqual(doc.comment, 'new comment')
        self.assertJSONEqual(response.content, {'status': 'success'})