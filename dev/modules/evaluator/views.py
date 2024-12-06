from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from core.uauth.models import UserMeta
from shared.mixins.mixins import UserRoleContextMixin
from modules.evaluator.forms import EvaluatorEditForm, EvaluatorPasswordChangeForm
from core.uauth.models import User
from modules.orders.models import *
from django.views.generic import TemplateView
from modules.orders.forms import *
from modules.evaluator.forms import *
from django.views import View
from django.http import JsonResponse

def index(request):
    return render(request, 'evaluator/index.html')

# This view is used for the evaluator to edit their own account. It is also used for the agency to edit the evaluator's account
class EditEvaluatorAccountView(LoginRequiredMixin, UserPassesTestMixin, UserRoleContextMixin, UpdateView):
    model = User
    form_class = EvaluatorEditForm
    template_name = 'edit_evaluator_account.html'
    success_url = reverse_lazy('modules.evaluator:edit_own_evaluator_account')
    login_url = 'core.uauth:login'
    redirect_field_name = 'next'

    def get_success_url(self):
        return reverse_lazy('modules.evaluator:edit_own_evaluator_account')

    def test_func(self):
        user = self.request.user
        return user.groups.filter(name__in=['Agency', 'Evaluator']).exists()

    def handle_no_permission(self):
        messages.error(self.request, "You do not have permission to access this page.")
        return redirect('core.uauth:login')

    def get_object(self, queryset=None):

        if self.request.user.groups.filter(name='Agency').exists() and 'pk' in self.kwargs:
            return User.objects.get(pk=self.kwargs['pk'])
        
        return self.request.user

    def get_initial(self):
        initial = super().get_initial()
        user = self.get_object()
        initial.update({
            'name': user.first_name,
            'last_name': user.last_name,
            'qualification_certificate_number': UserMeta.get_meta(user, 'qualification_certificate_number'),
            'date_of_issue_of_certificate': UserMeta.get_meta(user, 'date_of_issue_of_certificate'),
            'phone_num': UserMeta.get_meta(user, 'phone_num'),
        })
        return initial

    def form_valid(self, form):
        user = form.save()
        password_form = EvaluatorPasswordChangeForm(user, self.request.POST)

        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(self.request, user)
            messages.success(self.request, 'Your profile was successfully updated!')
        else:
            messages.error(self.request, 'Please correct the error below.')
            
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the error below.')
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['password_form'] = EvaluatorPasswordChangeForm(self.request.user)
        return context



# Acts as a hub for the multi-step evaluation process. This view provides the evaluator with the ability to see and navigate 
# through the evaluation steps
class EvaluationStepsView(LoginRequiredMixin, UserRoleContextMixin, TemplateView):
    template_name = "evaluation_steps.html"
    login_url = 'core.uauth:login'
    redirect_field_name = 'next'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_id = self.kwargs.get('order_id')
        order = get_object_or_404(Order, id=order_id)
        context['order'] = order
        return context
    


#This is the first of four views of the object data edit process. This view gets the order and object data and displays populated forms. 
#Is used for editing the data
class EditObjectDataView(LoginRequiredMixin, UserRoleContextMixin, UpdateView):
    model = Object
    template_name = 'edit_object.html'
    login_url = 'core.uauth:login'
    redirect_field_name = 'next'
    fields = []

    def get_object(self, queryset=None):
        return get_object_or_404(Object, pk=self.kwargs['pk'])

    def get_success_url(self):
        return reverse_lazy('modules.evaluator:edit_evaluation_decoration', kwargs={'order_id': self.kwargs['order_id'], 'pk': self.kwargs['pk']})

    def get_initial_data(self, obj):
        initial_data = {}
        meta_data = ObjectMeta.objects.filter(ev_object=obj)
        for meta in meta_data:
            initial_data[meta.meta_key] = meta.meta_value
        return initial_data

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.get_object()
        initial_data = self.get_initial_data(obj)
        context['location_form'] = ObjectLocationForm(initial=initial_data)
        if obj.object_type == 'Namas':
            context['additional_form'] = HouseForm(initial=initial_data)
        elif obj.object_type == 'Sklypas':
            context['additional_form'] = LandForm(initial=initial_data)
        elif obj.object_type == 'Butas':
            context['additional_form'] = ApartamentForm(initial=initial_data)
        elif obj.object_type == 'Kotedžas':
            context['additional_form'] = CottageForm(initial=initial_data)
        elif obj.object_type == 'Sodas':
            context['additional_form'] = HouseForm(initial=initial_data)
        context['order_id'] = self.kwargs['order_id']
        context['pk'] = self.kwargs['pk']
        context['current_step'] = 1
        context['total_steps'] = 8 
        return context

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        self.object = obj
        initial_data = self.get_initial_data(obj)
        location_form = ObjectLocationForm(request.POST, initial=initial_data)
        if obj.object_type == 'Namas':
            additional_form = HouseForm(request.POST, initial=initial_data)
        elif obj.object_type == 'Sklypas':
            additional_form = LandForm(request.POST, initial=initial_data)
        elif obj.object_type == 'Butas':
            additional_form = ApartamentForm(request.POST, initial=initial_data)
        elif obj.object_type == 'Kotedžas':
            additional_form = CottageForm(request.POST, initial=initial_data)
        elif obj.object_type == 'Sodas':
            additional_form = HouseForm(request.POST, initial=initial_data)
        else:
            additional_form = None
        if location_form.is_valid() and (additional_form is None or additional_form.is_valid()):
            self.save_form_data(obj, location_form.cleaned_data)
            if additional_form:
                self.save_form_data(obj, additional_form.cleaned_data)
            return redirect(self.get_success_url())
        return self.form_invalid(location_form, additional_form)

    def form_invalid(self, location_form, additional_form=None):
        context = self.get_context_data()
        context.update({
            'location_form': location_form,
        })
        if additional_form:
            context['additional_form'] = additional_form
        return self.render_to_response(context)

    def save_form_data(self, obj, cleaned_data):
        for key, value in cleaned_data.items():
            Object.save_meta(obj, key, value)



#This is the second of four views of the object data edit process. This view gets the order and object data and displays populated forms. 
#Is used for editing the data
class EditEvaluationAndDecoInfo(LoginRequiredMixin, UserRoleContextMixin, UpdateView):
    model = Object
    template_name = 'edit_evaluation_deco_info.html'
    login_url = 'core.uauth:login'
    redirect_field_name = 'next'
    fields = []

    def get_object(self, queryset=None):
        return get_object_or_404(Object, pk=self.kwargs['pk'])

    def get_success_url(self):
        return reverse_lazy('modules.evaluator:edit_common_info', kwargs={'order_id': self.kwargs['order_id'], 'pk': self.kwargs['pk']})

    def get_initial_data(self, obj):
        initial_data = {}
        meta_data = ObjectMeta.objects.filter(ev_object=obj)
        for meta in meta_data:
            initial_data[meta.meta_key] = meta.meta_value
        return initial_data

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.get_object()
        initial_data = self.get_initial_data(obj)
        context['decoration_form'] = DecorationForm(initial=initial_data)
        context['evaluation_form'] = EvaluationForm(initial=initial_data)
        context['order_id'] = self.kwargs['order_id']
        context['pk'] = self.kwargs['pk']
        context['current_step'] = 1
        context['total_steps'] = 8 
        return context

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        self.object = obj
        initial_data = self.get_initial_data(obj)
        decoration_form = DecorationForm(request.POST, initial=initial_data)
        evaluation_form = EvaluationForm(request.POST, initial=initial_data)
        
        if decoration_form.is_valid() and evaluation_form.is_valid():
            self.save_form_data(obj, decoration_form.cleaned_data)
            self.save_form_data(obj, evaluation_form.cleaned_data)
            return redirect(self.get_success_url())
        
        return self.form_invalid(decoration_form, evaluation_form)

    def form_invalid(self, decoration_form, evaluation_form):
        context = self.get_context_data()
        context.update({
            'decoration_form': decoration_form,
            'evaluation_form': evaluation_form,
        })
        return self.render_to_response(context)

    def save_form_data(self, obj, cleaned_data):
        for key, value in cleaned_data.items():
            Object.save_meta(obj, key, value)



#This is the third of four views of the object data edit process. This view gets the order and object data and displays populated forms. 
#Is used for editing the data
class EditCommonInfo(LoginRequiredMixin, UserRoleContextMixin, UpdateView):
    model = Object
    template_name = 'edit_common_info.html'
    login_url = 'core.uauth:login'
    redirect_field_name = 'next'
    fields = []

    def get_object(self, queryset=None):
        return get_object_or_404(Object, pk=self.kwargs['pk'])

    def get_success_url(self):
        return reverse_lazy('modules.evaluator:edit_utility_info', kwargs={'order_id': self.kwargs['order_id'], 'pk': self.kwargs['pk']})


    def get_initial_data(self, obj):
        initial_data = {}
        meta_data = ObjectMeta.objects.filter(ev_object=obj)
        for meta in meta_data:
            initial_data[meta.meta_key] = meta.meta_value
        return initial_data

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.get_object()
        initial_data = self.get_initial_data(obj)
        context['common_info_form'] = CommonInformationForm(initial=initial_data)
        context['order_id'] = self.kwargs['order_id']
        context['pk'] = self.kwargs['pk']
        context['current_step'] = 1
        context['total_steps'] = 8 
        return context

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        self.object = obj
        initial_data = self.get_initial_data(obj)
        common_info_form = CommonInformationForm(request.POST, initial=initial_data)
        
        if common_info_form.is_valid():
            self.save_form_data(obj, common_info_form.cleaned_data)
            return redirect(self.get_success_url())
        
        return self.form_invalid(common_info_form)

    def form_invalid(self, common_info_form):
        context = self.get_context_data()
        context.update({
            'common_info_form': common_info_form,
        })
        return self.render_to_response(context)

    def save_form_data(self, obj, cleaned_data):
        for key, value in cleaned_data.items():
            Object.save_meta(obj, key, value)



#This is the last of four views of the object data edit process. This view gets the order and object data and displays populated forms. 
#Is used for editing the data
class EditUtilityInfo(LoginRequiredMixin, UserRoleContextMixin, UpdateView):
    model = Object
    template_name = 'edit_utility_info.html'
    login_url = 'core.uauth:login'
    redirect_field_name = 'next'
    fields = []

    def get_object(self, queryset=None):
        return get_object_or_404(Object, pk=self.kwargs['pk'])

    def get_success_url(self):
        return reverse_lazy('modules.evaluator:edit_additional_buildings', kwargs={'order_id': self.kwargs['order_id'], 'pk': self.kwargs['pk']})

    def get_initial_data(self, obj):
        initial_data = {}
        meta_data = ObjectMeta.objects.filter(ev_object=obj)
        for meta in meta_data:
            initial_data[meta.meta_key] = meta.meta_value
        return initial_data

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.get_object()
        initial_data = self.get_initial_data(obj)
        context['utility_form'] = UtilityForm(initial=initial_data)
        context['order_id'] = self.kwargs['order_id']
        context['pk'] = self.kwargs['pk']
        context['current_step'] = 1
        context['total_steps'] = 8 
        return context

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        self.object = obj
        initial_data = self.get_initial_data(obj)
        utility_form = UtilityForm(request.POST, initial=initial_data)
        
        if utility_form.is_valid():
            self.save_form_data(obj, utility_form.cleaned_data)
            return redirect(self.get_success_url())
        
        return self.form_invalid(utility_form)

    def form_invalid(self, utility_form):
        context = self.get_context_data()
        context.update({
            'utility_form': utility_form,
        })
        return self.render_to_response(context)

    def save_form_data(self, obj, cleaned_data):
        for key, value in cleaned_data.items():
            Object.save_meta(obj, key, value)



# Second step of the evaluation process. This view provides the evaluator with the ability 
# to edit objects additional buildings data. Only the associated additional buildings are loaded
class EvaluatorEditAdditionalBuildings(LoginRequiredMixin, UserRoleContextMixin, UpdateView):
    model = Object
    template_name = "edit_additional_buildings.html"
    login_url = 'core.uauth:login'
    redirect_field_name = 'next'
    fields = []

    def get_object(self, queryset=None):
        return get_object_or_404(Object, pk=self.kwargs['pk'])

    def get_success_url(self):
        return reverse_lazy('modules.evaluator:edit_RC_data', kwargs={'order_id': self.kwargs['order_id'], 'pk': self.kwargs['pk']})

    def get_forms(self):
        obj = self.get_object()
        garage_data = ObjectMeta.objects.filter(ev_object=obj, meta_key__startswith='garage_')
        shed_data = ObjectMeta.objects.filter(ev_object=obj, meta_key__startswith='shed_')
        gazebo_data = ObjectMeta.objects.filter(ev_object=obj, meta_key__startswith='gazebo_')
        
        forms = {}

        if garage_data.exists():
            garage_initial = {meta.meta_key: meta.meta_value for meta in garage_data}
            forms['garage_form'] = GarageForm(initial=garage_initial, prefix='garage')

        if shed_data.exists():
            shed_initial = {meta.meta_key: meta.meta_value for meta in shed_data}
            forms['shed_form'] = ShedForm(initial=shed_initial, prefix='shed')

        if gazebo_data.exists():
            gazebo_initial = {meta.meta_key: meta.meta_value for meta in gazebo_data}
            forms['gazebo_form'] = GazeboForm(initial=gazebo_initial, prefix='gazebo')

        return forms

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_forms())
        context['order_id'] = self.kwargs['order_id']
        context['pk'] = self.kwargs['pk']
        context['show_progress_bar'] = True
        context['is_evaluator'] = True
        context['current_step'] = 2
        context['total_steps'] = 8 
        return context

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        self.object = obj
        forms = self.get_forms()
        all_valid = True

        for form_name, form in forms.items():
            form_instance = form.__class__(request.POST, prefix=form.prefix)

            if not form_instance.is_valid():
                all_valid = False
                forms[form_name] = form_instance
                break

        if all_valid:
            for form_name, form in forms.items():
                form_instance = form.__class__(request.POST, prefix=form.prefix)

                if form_instance.is_valid():
                    self.save_form_data(obj, form_instance.cleaned_data)

            return redirect(self.get_success_url())
        
        return self.form_invalid(forms)

    def form_invalid(self, forms):
        context = self.get_context_data()
        context.update(forms)
        return self.render_to_response(context)

    def save_form_data(self, obj, cleaned_data):
        for key, value in cleaned_data.items():
            Object.save_meta(obj, key, value)



# Third step of the evaluation process. This view should be responsible for getting and displaying data from "Registru Centras".
# For now it is just a placeholder
class RCDataEditView(LoginRequiredMixin, UserRoleContextMixin, TemplateView):
    template_name = "edit_RC_data.html"
    login_url = 'core.uauth:login'
    redirect_field_name = 'next'

    def get_success_url(self):
        return reverse_lazy('modules.evaluator:edit_gallery', kwargs={'order_id': self.kwargs['order_id'], 'pk': self.kwargs['pk']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_id = self.kwargs.get('order_id')
        order = get_object_or_404(Order, id=order_id)
        obj = order.object
        client = order.client
        phone_number = UserMeta.get_meta(client, 'phone_num')
        context['order'] = order
        context['object'] = obj
        context['client'] = client
        context['phone_number'] = phone_number
        context['order_id'] = self.kwargs['order_id']
        context['pk'] = self.kwargs['pk']
        context['show_progress_bar'] = True
        context['is_evaluator'] = True
        context['current_step'] = 3
        context['total_steps'] = 8 

        return context
    


class EditObjectGalleryView(LoginRequiredMixin, UserRoleContextMixin, TemplateView):
    template_name = "object_gallery.html"
    login_url = 'core.uauth:login'
    redirect_field_name = 'next'

    def get_success_url(self):
        return reverse_lazy('modules.evaluator:evaluation_steps', kwargs={'order_id': self.kwargs['order_id']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_id = self.kwargs.get('order_id')
        order = get_object_or_404(Order, id=order_id)
        obj = order.object
        client = order.client
        phone_number = UserMeta.get_meta(client, 'phone_num')
        context['order'] = order
        context['object'] = obj
        context['client'] = client
        context['phone_number'] = phone_number
        context['order_id'] = self.kwargs['order_id']
        context['pk'] = self.kwargs['pk']
        context['show_progress_bar'] = True
        context['is_evaluator'] = True
        context['current_step'] = 4
        context['total_steps'] = 8 
        context['image_form'] = ObjectImageForm()
        context['images'] = obj.images.all()
        return context

    def post(self, request, *args, **kwargs):
        order_id = self.kwargs.get('order_id')
        order = get_object_or_404(Order, id=order_id)
        obj = order.object
        if 'upload_image' in request.POST:
            image_form = ObjectImageForm(request.POST, request.FILES)
            if image_form.is_valid():
                image = image_form.save(commit=False)
                image.object = obj
                image.save()
                return redirect(self.get_success_url())
        elif 'delete_image' in request.POST:
            image_id = request.POST.get('image_id')
            image = get_object_or_404(ObjectImage, id=image_id)
            image.delete()
            return redirect(self.get_success_url())
        return self.get(request, *args, **kwargs)
    


class ImageAnnotationView(LoginRequiredMixin, UserRoleContextMixin, TemplateView):
    template_name = "image_annotation.html"
    login_url = 'core.uauth:login'
    redirect_field_name = 'next'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_id = self.kwargs.get('order_id')
        image_id = self.kwargs.get('image_id')
        order = get_object_or_404(Order, id=order_id)
        image = get_object_or_404(ObjectImage, id=image_id, object=order.object)
        context['order'] = order
        context['image'] = image
        context['annotation_form'] = ImageAnnotationForm()
        context['annotations'] = image.annotations.all()
        return context

    def post(self, request, *args, **kwargs):
        order_id = self.kwargs.get('order_id')
        image_id = self.kwargs.get('image_id')
        order = get_object_or_404(Order, id=order_id)
        image = get_object_or_404(ObjectImage, id=image_id, object=order.object)
        annotation_form = ImageAnnotationForm(request.POST, request.FILES)
        if annotation_form.is_valid():
            annotation = annotation_form.save(commit=False)
            annotation.image = image
            annotation.save()
            return redirect('modules.evaluator:image_annotation', order_id=order_id, image_id=image_id)
        context = self.get_context_data(**kwargs)
        context['annotation_form'] = annotation_form
        return self.render_to_response(context)
    

class AnnotationDetailView(View):
    def get(self, request, annotation_id):
        annotation = get_object_or_404(ImageAnnotation, id=annotation_id)
        data = {
            'annotation_text': annotation.annotation_text,
            'annotation_image': annotation.annotation_image.url if annotation.annotation_image else None,
        }
        print(data)
        return JsonResponse(data)