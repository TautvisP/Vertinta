from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from modules.orders.models import Object, Order, ObjectImage, ImageAnnotation
from core.uauth.models import UserMeta
from modules.orders.models import ObjectMeta


User = get_user_model()

class ObjectGalleryViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='eval@example.com', password='pass', first_name='Eval', last_name='User'
        )
        self.client.login(email='eval@example.com', password='pass')
        self.object = Object.objects.create(object_type='Namas', latitude=55.0, longitude=25.0)
        ObjectMeta.objects.create(ev_object=self.object, meta_key='municipality', meta_value='1')
        self.order = Order.objects.create(
            client=self.user,
            evaluator=self.user,
            object=self.object,
            status='Naujas'
        )
        self.image = ObjectImage.objects.create(object=self.object, image=SimpleUploadedFile("test.jpg", b"filecontent", content_type="image/jpeg"))
        self.annotation = ImageAnnotation.objects.create(
            image=self.image,
            annotation_text="Test annotation",
            x_coordinate=10,
            y_coordinate=20
        )

    def test_gallery_view_get(self):
        url = reverse('modules.evaluator:edit_gallery', args=[self.order.id, self.object.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('image_form', response.context)
        self.assertIn('images', response.context)

    def test_upload_image(self):
        url = reverse('modules.evaluator:edit_gallery', args=[self.order.id, self.object.id])
        image = SimpleUploadedFile("test.jpg", b"filecontent", content_type="image/jpeg")
        response = self.client.post(url, {'upload_image': '1', 'image': image})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(ObjectImage.objects.filter(object=self.object).exists())

    def test_delete_image(self):
        url = reverse('modules.evaluator:delete_image', args=[self.order.id, self.image.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(ObjectImage.objects.filter(id=self.image.id).exists())

    def test_image_annotation_view_get(self):
        url = reverse('modules.evaluator:image_annotation', args=[self.order.id, self.image.id, self.object.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('annotation_form', response.context)
        self.assertIn('annotations', response.context)

    def test_create_annotation(self):
        url = reverse('modules.evaluator:create_annotation', args=[self.order.id, self.image.id, self.object.id])
        data = {
            'annotation_text': 'Another annotation',
            'x_coordinate': 15,
            'y_coordinate': 25,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(ImageAnnotation.objects.filter(image=self.image, annotation_text='Another annotation').exists())

    def test_delete_annotation(self):
        url = reverse('modules.evaluator:delete_annotation', args=[self.annotation.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(ImageAnnotation.objects.filter(id=self.annotation.id).exists())

    def test_edit_annotation(self):
        url = reverse('modules.evaluator:edit_annotation', args=[self.annotation.id])
        data = {
            'annotation_text': 'Edited annotation',
            'x_coordinate': 30,
            'y_coordinate': 40,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.annotation.refresh_from_db()
        self.assertEqual(self.annotation.annotation_text, 'Edited annotation')

    def test_annotation_detail_view(self):
        url = reverse('modules.evaluator:annotation_detail', args=[self.annotation.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('annotation_text', response.json())