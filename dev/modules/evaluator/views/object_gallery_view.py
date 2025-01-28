""""
Contains logic for objects image gallery and image annotations.
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

# Global context variables
TOTAL_STEPS = 8
SHOW_PROGRESS_BAR = True




class EditObjectGalleryView(LoginRequiredMixin, UserRoleContextMixin, TemplateView):
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
            
        elif 'delete_image' in request.POST:
            image_id = request.POST.get('image_id')
            image = get_object_or_404(self.image_model, id=image_id)
            image.delete()
            return redirect(self.get_success_url())
        
        return self.get(request, *args, **kwargs)




class ImageAnnotationView(LoginRequiredMixin, UserRoleContextMixin, TemplateView):
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
            return redirect('modules.evaluator:image_annotation', order_id=order_id, image_id=image_id, pk=order.object.id)
        
        context = self.get_context_data(**kwargs)
        context['annotation_form'] = annotation_form
        return self.render_to_response(context)
    



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
        print(data)
        return JsonResponse(data)