from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from modules.orders.models import Object, Order, ObjectImage, ImageAnnotation, ObjectMeta
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import Group


User = get_user_model()

class ObjectGalleryViewIntegrationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='eval@example.com', password='pass', first_name='Eval', last_name='User'
        )
        evaluator_group, _ = Group.objects.get_or_create(name='Evaluator')
        self.user.groups.add(evaluator_group)
        self.client.login(email='eval@example.com', password='pass')
        self.object = Object.objects.create(object_type='Namas', latitude=55.0, longitude=25.0)
        self.order = Order.objects.create(
            client=self.user,
            evaluator=self.user,
            object=self.object,
            status='Naujas'
        )
        ObjectMeta.objects.create(ev_object=self.object, meta_key='municipality', meta_value='1')


    def test_gallery_get(self):
        url = reverse('modules.evaluator:edit_gallery', kwargs={'order_id': self.order.id, 'pk': self.object.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('images', response.context)

    def test_image_upload(self):
        url = reverse('modules.evaluator:edit_gallery', kwargs={'order_id': self.order.id, 'pk': self.object.id})
        img = SimpleUploadedFile("test.jpg", b"filecontent", content_type="image/jpeg")
        data = {'upload_image': '1', 'image': img}
        response = self.client.post(url, data, format='multipart')
        self.assertEqual(response.status_code, 200)

    def test_create_annotation(self):
        image = ObjectImage.objects.create(object=self.object, image=SimpleUploadedFile("test.jpg", b"filecontent", content_type="image/jpeg"))
        url = reverse('modules.evaluator:create_annotation', kwargs={
            'order_id': self.order.id,
            'image_id': image.id,
            'pk': self.object.id
        })
        data = {
            'annotation_text': 'Test annotation',
            'x_coordinate': 0.5,
            'y_coordinate': 0.5,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(ImageAnnotation.objects.filter(image=image, annotation_text='Test annotation').exists())

    def test_edit_annotation(self):
        image = ObjectImage.objects.create(object=self.object, image=SimpleUploadedFile("test.jpg", b"filecontent", content_type="image/jpeg"))
        annotation = ImageAnnotation.objects.create(image=image, annotation_text='Old text', x_coordinate=0.1, y_coordinate=0.2)
        url = reverse('modules.evaluator:edit_annotation', args=[annotation.id])
        data = {
            'annotation_text': 'Updated text',
            'x_coordinate': 0.1,
            'y_coordinate': 0.2,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        annotation.refresh_from_db()
        self.assertEqual(annotation.annotation_text, 'Updated text')

    def test_delete_annotation(self):
        image = ObjectImage.objects.create(object=self.object, image=SimpleUploadedFile("test.jpg", b"filecontent", content_type="image/jpeg"))
        annotation = ImageAnnotation.objects.create(image=image, annotation_text='To delete', x_coordinate=0.1, y_coordinate=0.2)
        url = reverse('modules.evaluator:delete_annotation', args=[annotation.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(ImageAnnotation.objects.filter(id=annotation.id).exists())

    def test_annotation_detail_view(self):
        image = ObjectImage.objects.create(object=self.object, image=SimpleUploadedFile("test.jpg", b"filecontent", content_type="image/jpeg"))
        annotation = ImageAnnotation.objects.create(image=image, annotation_text='Detail text', x_coordinate=0.1, y_coordinate=0.2)
        url = reverse('modules.evaluator:annotation_detail', args=[annotation.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['annotation_text'], 'Detail text')