""""
Contains logic for objects image gallery and image annotations.
Image annotations are displayed on the image and can be edited or deleted.
They have coordinates and text and or an image.
"""

from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from core.uauth.models import UserMeta
from shared.mixins.mixins import UserRoleContextMixin
from modules.orders.models import Order, ObjectImage, ImageAnnotation
from django.views.generic import TemplateView
from modules.evaluator.forms import ObjectImageForm, ImageAnnotationForm
from django.views import View
from django.http import JsonResponse
from django.utils.translation import gettext as _
from shared.mixins.evaluator_access_mixin import EvaluatorAccessMixin


# Global context variables
TOTAL_STEPS = 8
SHOW_PROGRESS_BAR = True


class EditObjectGalleryView(LoginRequiredMixin, EvaluatorAccessMixin, UserRoleContextMixin, TemplateView):
    """
    This view is responsible for displaying the object gallery page.
    Handles image upload and deletion
    """

    model = Order
    user_meta = UserMeta
    image_model = ObjectImage
    template_name = "object_gallery.html"
    login_url = 'core.uauth:login'
    redirect_field_name = 'next'

    form_class_image = ObjectImageForm

    def get_success_url(self):
        return reverse_lazy('modules.evaluator:edit_gallery', kwargs={'order_id': self.kwargs['order_id'], 'pk': self.kwargs['pk']})


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_id = self.kwargs.get('order_id')
        order = get_object_or_404(self.model, id=order_id)
        obj = order.object
        client = order.client
        phone_number = self.user_meta.get_meta(client, 'phone_num')
        context['order'] = order
        context['object'] = obj
        context['client'] = client
        context['phone_number'] = phone_number
        context['order_id'] = self.kwargs['order_id']
        context['pk'] = self.kwargs['pk']
        context['show_progress_bar'] = SHOW_PROGRESS_BAR
        context['is_evaluator'] = True
        context['current_step'] = 4
        context['total_steps'] = TOTAL_STEPS
        context['image_form'] = self.form_class_image()
        context['images'] = obj.images.all()
        return context


    def post(self, request, *args, **kwargs):
        order_id = self.kwargs.get('order_id')
        order = get_object_or_404(self.model, id=order_id)
        obj = order.object

        if 'upload_image' in request.POST:
            image_form = self.form_class_image(request.POST, request.FILES)

            if image_form.is_valid():
                image = image_form.save(commit=False)
                image.object = obj
                image.save()
                return redirect(self.get_success_url())
        
        return self.get(request, *args, **kwargs)
    



class DeleteObjectImageView(LoginRequiredMixin, EvaluatorAccessMixin, UserRoleContextMixin, View):
    """
    View to handle the deletion of an object image along with its annotations.
    Requires the user to be logged in and have the appropriate role.
    """
    def post(self, request, *args, **kwargs):
        order_id = self.kwargs.get('order_id')
        image_id = self.kwargs.get('image_id')
        order = get_object_or_404(Order, id=order_id)
        image = get_object_or_404(ObjectImage, id=image_id, object=order.object)

        image.annotations.all().delete()
        image.delete()

        return JsonResponse({'status': 'success', 'message': 'Nuotrauka sėkmingai ištrinta.'})




class ImageAnnotationView(LoginRequiredMixin, EvaluatorAccessMixin, UserRoleContextMixin, TemplateView):
    """
    This view is responsible for displaying the image annotation page.
    Validates the form and saves the annotation to the database
    """

    model = Order
    model_image = ObjectImage
    template_name = "image_annotation.html"
    login_url = 'core.uauth:login'
    redirect_field_name = 'next'
    form_class_annotation = ImageAnnotationForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_id = self.kwargs.get('order_id')
        image_id = self.kwargs.get('image_id')
        pk = self.kwargs.get('pk')
        order = get_object_or_404(self.model, id=order_id)
        image = get_object_or_404(self.model_image, id=image_id, object=order.object)
        context['order'] = order
        context['image'] = image
        context['annotation_form'] = self.form_class_annotation()
        context['annotations'] = image.annotations.all()
        context['pk'] = pk
        return context




class CreateAnnotationView(LoginRequiredMixin, EvaluatorAccessMixin, UserRoleContextMixin, View):
    """
    This view is responsible for creating a new annotation.
    """
    model = Order
    model_image = ObjectImage
    form_class_annotation = ImageAnnotationForm

    def post(self, request, *args, **kwargs):
        order_id = self.kwargs.get('order_id')
        image_id = self.kwargs.get('image_id')
        order = get_object_or_404(self.model, id=order_id)
        image = get_object_or_404(self.model_image, id=image_id, object=order.object)
        annotation_form = self.form_class_annotation(request.POST, request.FILES)

        if annotation_form.is_valid():
            annotation = annotation_form.save(commit=False)
            annotation.image = image
            annotation.save()
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                response_data = {'status': 'success'}
                return JsonResponse(response_data, content_type='application/json')
            return redirect('modules.evaluator:image_annotation', order_id=order_id, image_id=image_id, pk=order.object.id)
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            response_data = {'status': 'error', 'errors': annotation_form.errors}
            return JsonResponse(response_data, content_type='application/json')
        
        return redirect('modules.evaluator:image_annotation', order_id=order_id, image_id=image_id, pk=order.object.id)




class DeleteAnnotationView(LoginRequiredMixin, UserRoleContextMixin, View):
    """
    View to handle the deletion of an image annotation.
    Requires the user to be logged in and have the appropriate role.
    """
    def delete(self, request, annotation_id):
        annotation = get_object_or_404(ImageAnnotation, id=annotation_id)
        annotation.delete()
        return JsonResponse({'status': 'success'})




class EditAnnotationView(LoginRequiredMixin, UserRoleContextMixin, View):
    """
    View to handle the editing of an image annotation.
    Requires the user to be logged in and have the appropriate role.
    """
    def post(self, request, annotation_id):
        annotation = get_object_or_404(ImageAnnotation, id=annotation_id)
        data = request.POST.copy()
        
        # Retain original coordinates if not provided
        if 'x_coordinate' not in data or not data['x_coordinate']:
            data['x_coordinate'] = annotation.x_coordinate
        if 'y_coordinate' not in data or not data['y_coordinate']:
            data['y_coordinate'] = annotation.y_coordinate

        annotation_form = ImageAnnotationForm(data, request.FILES, instance=annotation)

        if annotation_form.is_valid():
            annotation_form.save()
            return JsonResponse({'status': 'success'})
        return JsonResponse({'status': 'error', 'errors': annotation_form.errors})




class AnnotationDetailView(View):
    """
    This is responsible for loading modal window of annotation information when an annotation is clicked
    """

    def get(self, request, annotation_id):
        annotation = get_object_or_404(ImageAnnotation, id=annotation_id)
        data = {
            'annotation_text': annotation.annotation_text,
            'annotation_image': annotation.annotation_image.url if annotation.annotation_image else None,
        }
        return JsonResponse(data)