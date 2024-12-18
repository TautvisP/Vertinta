from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic.edit import UpdateView
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from core.uauth.models import UserMeta
from shared.mixins.mixins import UserRoleContextMixin
from core.uauth.models import User
from modules.orders.models import Object, Order, ObjectImage, ImageAnnotation, ObjectMeta, SimilarObject, SimilarObjectMetadata
from django.views.generic import TemplateView
from modules.orders.forms import ObjectLocationForm, HouseForm, LandForm, ApartamentForm, CottageForm, DecorationForm, CommonInformationForm, UtilityForm, GarageForm, ShedForm, GazeboForm
from modules.evaluator.forms import EvaluatorEditForm, EvaluatorPasswordChangeForm, EvaluationForm, SimilarObjectTypeSelectionForm, ObjectImageForm, ImageAnnotationForm, ButasSearchForm, NamasSearchForm, PatalposSearchForm, SklypaiSearchForm, SimilarObjectForm
from django.views import View
from django.http import JsonResponse
from django.utils.translation import gettext as _


from django.template.loader import render_to_string
import requests
from bs4 import BeautifulSoup
from django.http import JsonResponse, HttpResponseBadRequest


# Global message variables
SUCCESS_MESSAGE = _("Profilis sėkmingai atnaujintas!")
MISTAKE_MESSAGE = _("Pataisykite klaidas.")
NO_PERMISSION_MESSAGE = _("Neturite leidimo pasiekti šį puslapį.")


def index(request):
    return render(request, 'evaluator/index.html')




class EditEvaluatorAccountView(LoginRequiredMixin, UserPassesTestMixin, UserRoleContextMixin, UpdateView):
    """
    This view is used for the evaluator to edit their own account. It is also used for the agency to edit the evaluator's account
    """

    model = User
    model_meta = UserMeta
    form_class = EvaluatorEditForm
    form_class_password = EvaluatorPasswordChangeForm
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
        messages.error(self.request, NO_PERMISSION_MESSAGE)
        return redirect('core.uauth:login')


    def get_object(self, queryset=None):

        if self.request.user.groups.filter(name='Agency').exists() and 'pk' in self.kwargs:
            return self.model.objects.get(pk=self.kwargs['pk'])
        
        return self.request.user


    def get_initial(self):
        initial = super().get_initial()
        user = self.get_object()
        initial.update({
            'name': user.first_name,
            'last_name': user.last_name,
            'qualification_certificate_number': UserMeta.get_meta(user, 'qualification_certificate_number'),
            'date_of_issue_of_certificate': UserMeta.get_meta(user, 'date_of_issue_of_certificate'),
            'phone_num': self.model_meta.get_meta(user, 'phone_num'),
        })
        return initial


    def form_valid(self, form):
        user = form.save()
        password_form = self.form_class_password(user, self.request.POST)

        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(self.request, user)
            messages.success(self.request, SUCCESS_MESSAGE)
        else:
            messages.error(self.request, MISTAKE_MESSAGE)
            
        return super().form_valid(form)


    def form_invalid(self, form):
        messages.error(self.request, MISTAKE_MESSAGE)
        return super().form_invalid(form)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['password_form'] = self.form_class_password(self.request.user)
        return context




class EvaluationStepsView(LoginRequiredMixin, UserRoleContextMixin, TemplateView):
    """
    Acts as a hub for the multi-step evaluation process. 
    This view provides the evaluator with the ability to see and navigate through the evaluation steps
    """

    template_name = "evaluation_steps.html"
    login_url = 'core.uauth:login'
    redirect_field_name = 'next'


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_id = self.kwargs.get('order_id')
        order = get_object_or_404(Order, id=order_id)
        context['order'] = order
        return context
    



class EditObjectDataView(LoginRequiredMixin, UserRoleContextMixin, UpdateView):
    """
    This is the first of four views of the object data edit process. This view gets the order and object data and displays populated forms. 
    Is used for editing the data
    """

    model = Object
    model_meta = ObjectMeta
    template_name = 'edit_object.html'
    login_url = 'core.uauth:login'
    redirect_field_name = 'next'
    fields = []

    form_class_location = ObjectLocationForm
    form_class_house = HouseForm
    form_class_land = LandForm
    form_class_apartament = ApartamentForm
    form_class_cottage = CottageForm

    def get_object(self, queryset=None):
        return get_object_or_404(self.model, pk=self.kwargs['pk'])


    def get_success_url(self):
        return reverse_lazy('modules.evaluator:edit_evaluation_decoration', kwargs={'order_id': self.kwargs['order_id'], 'pk': self.kwargs['pk']})


    def get_initial_data(self, obj):
        initial_data = {}
        meta_data = self.model_meta.objects.filter(ev_object=obj)

        for meta in meta_data:
            initial_data[meta.meta_key] = meta.meta_value
        return initial_data


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.get_object()
        initial_data = self.get_initial_data(obj)
        context['location_form'] = self.form_class_location(initial=initial_data)

        match obj.object_type:
            case 'Namas':
                context['additional_form'] = self.form_class_house(initial=initial_data)

            case 'Sklypas':
                context['additional_form'] = self.form_class_land(initial=initial_data)

            case 'Butas':
                context['additional_form'] = self.form_class_apartament(initial=initial_data)

            case 'Kotedžas':
                context['additional_form'] = self.form_class_cottage(initial=initial_data)

            case 'Sodas':
                context['additional_form'] = self.form_class_house(initial=initial_data)


        context['order_id'] = self.kwargs['order_id']
        context['pk'] = self.kwargs['pk']
        context['current_step'] = 1
        context['total_steps'] = 8 
        context['show_progress_bar'] = True
        return context


    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        self.object = obj
        initial_data = self.get_initial_data(obj)
        location_form = self.form_class_location(request.POST, initial=initial_data)

        match obj.object_type:
            case 'Namas':
                additional_form = self.form_class_house(request.POST, initial=initial_data)

            case 'Sklypas':
                additional_form = self.form_class_land(request.POST, initial=initial_data)

            case 'Butas':
                additional_form = self.form_class_apartament(request.POST, initial=initial_data)

            case 'Kotedžas':
                additional_form = self.form_class_cottage(request.POST, initial=initial_data)

            case 'Sodas':
                additional_form = self.form_class_house(request.POST, initial=initial_data)

            case _:
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
            self.model.save_meta(obj, key, value)





class EditEvaluationAndDecoInfo(LoginRequiredMixin, UserRoleContextMixin, UpdateView):
    """
    This is the second of four views of the object data edit process. This view gets the order and object data and displays populated forms. 
    Is used for editing the data.
    """

    model = Object
    model_meta = ObjectMeta
    template_name = 'edit_evaluation_deco_info.html'
    login_url = 'core.uauth:login'
    redirect_field_name = 'next'
    fields = []

    form_class_decoration = DecorationForm
    form_class_evaluation = EvaluationForm

    def get_object(self, queryset=None):
        return get_object_or_404(self.model, pk=self.kwargs['pk'])


    def get_success_url(self):
        return reverse_lazy('modules.evaluator:edit_common_info', kwargs={'order_id': self.kwargs['order_id'], 'pk': self.kwargs['pk']})


    def get_initial_data(self, obj):
        initial_data = {}
        meta_data = self.model_meta.objects.filter(ev_object=obj)

        for meta in meta_data:
            initial_data[meta.meta_key] = meta.meta_value

        return initial_data


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.get_object()
        initial_data = self.get_initial_data(obj)
        context['decoration_form'] = self.form_class_decoration(initial=initial_data)
        context['evaluation_form'] = self.form_class_evaluation(initial=initial_data)
        context['order_id'] = self.kwargs['order_id']
        context['pk'] = self.kwargs['pk']
        context['current_step'] = 1
        context['total_steps'] = 8 
        context['show_progress_bar'] = True
        return context


    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        self.object = obj
        initial_data = self.get_initial_data(obj)
        decoration_form = self.form_class_decoration(request.POST, initial=initial_data)
        evaluation_form = self.form_class_evaluation(request.POST, initial=initial_data)
        
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
            self.model.save_meta(obj, key, value)




class EditCommonInfo(LoginRequiredMixin, UserRoleContextMixin, UpdateView):
    """
    This is the third of four views of the object data edit process. This view gets the order and object data and displays populated forms. 
    Is used for editing the data.
    """

    model = Object
    model_meta = ObjectMeta
    template_name = 'edit_common_info.html'
    login_url = 'core.uauth:login'
    redirect_field_name = 'next'
    fields = []

    form_class_common_info = CommonInformationForm

    def get_object(self, queryset=None):
        return get_object_or_404(self.model, pk=self.kwargs['pk'])


    def get_success_url(self):
        return reverse_lazy('modules.evaluator:edit_utility_info', kwargs={'order_id': self.kwargs['order_id'], 'pk': self.kwargs['pk']})


    def get_initial_data(self, obj):
        initial_data = {}
        meta_data = self.model_meta.objects.filter(ev_object=obj)

        for meta in meta_data:
            initial_data[meta.meta_key] = meta.meta_value

        return initial_data


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.get_object()
        initial_data = self.get_initial_data(obj)
        context['common_info_form'] = self.form_class_common_info(initial=initial_data)
        context['order_id'] = self.kwargs['order_id']
        context['pk'] = self.kwargs['pk']
        context['current_step'] = 1
        context['total_steps'] = 8 
        context['show_progress_bar'] = True
        return context


    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        self.object = obj
        initial_data = self.get_initial_data(obj)
        common_info_form = self.form_class_common_info(request.POST, initial=initial_data)
        
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
            self.model.save_meta(obj, key, value)






class EditUtilityInfo(LoginRequiredMixin, UserRoleContextMixin, UpdateView):
    """
    This is the last of four views of the object data edit process. This view gets the order and object data and displays populated forms. 
    Is used for editing the data
    """

    model = Object
    model_meta = ObjectMeta
    template_name = 'edit_utility_info.html'
    login_url = 'core.uauth:login'
    redirect_field_name = 'next'
    fields = []

    form_class_utility = UtilityForm

    def get_object(self, queryset=None):
        return get_object_or_404(self.model, pk=self.kwargs['pk'])


    def get_success_url(self):
        return reverse_lazy('modules.evaluator:edit_additional_buildings', kwargs={'order_id': self.kwargs['order_id'], 'pk': self.kwargs['pk']})


    def get_initial_data(self, obj):
        initial_data = {}
        meta_data = self.model_meta.objects.filter(ev_object=obj)

        for meta in meta_data:
            initial_data[meta.meta_key] = meta.meta_value

        return initial_data


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.get_object()
        initial_data = self.get_initial_data(obj)
        context['utility_form'] = self.form_class_utility(initial=initial_data)
        context['order_id'] = self.kwargs['order_id']
        context['pk'] = self.kwargs['pk']
        context['current_step'] = 1
        context['total_steps'] = 8 
        context['show_progress_bar'] = True
        return context


    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        self.object = obj
        initial_data = self.get_initial_data(obj)
        utility_form = self.form_class_utility(request.POST, initial=initial_data)
        
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
            self.model.save_meta(obj, key, value)




class EvaluatorEditAdditionalBuildings(LoginRequiredMixin, UserRoleContextMixin, UpdateView):
    """
    Second step of the evaluation process. This view provides the evaluator with the ability 
    to edit objects additional buildings data. Only the associated additional buildings are loaded.
    """

    model = Object
    model_meta = ObjectMeta
    template_name = "edit_additional_buildings.html"
    login_url = 'core.uauth:login'
    redirect_field_name = 'next'
    fields = []
    
    form_class_garage = GarageForm
    form_class_shed = ShedForm
    form_class_gazebo = GazeboForm


    def get_object(self, queryset=None):
        return get_object_or_404(self.model, pk=self.kwargs['pk'])


    def get_success_url(self):
        return reverse_lazy('modules.evaluator:edit_RC_data', kwargs={'order_id': self.kwargs['order_id'], 'pk': self.kwargs['pk']})


    def get_forms(self):
        obj = self.get_object()
        garage_data = self.model_meta.objects.filter(ev_object=obj, meta_key__startswith='garage_')
        shed_data = self.model_meta.objects.filter(ev_object=obj, meta_key__startswith='shed_')
        gazebo_data = self.model_meta.objects.filter(ev_object=obj, meta_key__startswith='gazebo_')
        
        forms = {}

        if garage_data.exists():
            garage_initial = {meta.meta_key: meta.meta_value for meta in garage_data}
            forms['garage_form'] = self.form_class_garage(initial=garage_initial, prefix='garage')

        if shed_data.exists():
            shed_initial = {meta.meta_key: meta.meta_value for meta in shed_data}
            forms['shed_form'] = self.form_class_shed(initial=shed_initial, prefix='shed')

        if gazebo_data.exists():
            gazebo_initial = {meta.meta_key: meta.meta_value for meta in gazebo_data}
            forms['gazebo_form'] = self.form_class_gazebo(initial=gazebo_initial, prefix='gazebo')

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
            self.model.save_meta(obj, key, value)




class RCDataEditView(LoginRequiredMixin, UserRoleContextMixin, TemplateView):
    """
    Third step of the evaluation process. This view should be responsible for getting and displaying data from "Registru Centras".
    For now it is just a placeholder
    """

    model = Object
    user_meta = UserMeta
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
        phone_number = self.user_meta.get_meta(client, 'phone_num')
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
        context['show_progress_bar'] = True
        context['is_evaluator'] = True
        context['current_step'] = 4
        context['total_steps'] = 8 
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
        order = get_object_or_404(self.model, id=order_id)
        image = get_object_or_404(self.model_image, id=image_id, object=order.object)
        context['order'] = order
        context['image'] = image
        context['annotation_form'] = self.form_class_annotation()
        context['annotations'] = image.annotations.all()
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
            return redirect('modules.evaluator:image_annotation', order_id=order_id, image_id=image_id)
        
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
    



class SimilarObjectSearchView(LoginRequiredMixin, UserRoleContextMixin, TemplateView):
    """
    This function still needs to be developed. Currently aruodas scraper is not working because of the human verification
    """

    model_meta = UserMeta
    template_name = 'similar_object_search.html'
    result_template_name = 'similar_object_results.html'
    login_url = 'core.uauth:login'
    redirect_field_name = 'next'

    form_class_object_type = SimilarObjectTypeSelectionForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_id = self.kwargs.get('order_id')
        pk = self.kwargs.get('pk')
        order = get_object_or_404(Order, id=order_id)
        obj = get_object_or_404(Object, id=pk)
        client = order.client
        phone_number = self.model_meta.get_meta(client, 'phone_num')
        context['order'] = order
        context['object'] = obj
        context['client'] = client
        context['phone_number'] = phone_number
        context['order_id'] = order_id
        context['pk'] = pk
        context['show_progress_bar'] = True
        context['is_evaluator'] = True
        context['current_step'] = 5
        context['total_steps'] = 8
        context['form'] = self.form_class_object_type()
        return context


    def post(self, request, *args, **kwargs):
        order_id = self.kwargs.get('order_id')
        pk = self.kwargs.get('pk')
        object_type = request.POST.get('object_type')
        # print(f"POST request received with object_type: {object_type}")  # Debugging statement
        form_class = self.get_form_class(object_type)

        if form_class is None:
            print(f"Invalid object type: {object_type}")  # Debugging statement
            return HttpResponseBadRequest(f"Invalid object type: {object_type}")
        
        form = form_class(request.POST)
        context = self.get_context_data(order_id=order_id, pk=pk)
        
        if form.is_valid():
            data = form.cleaned_data
            listings = self.scrape_aruodas(data, object_type)
            context['form'] = form
            context['listings'] = listings
            return render(request, self.result_template_name, context)
        
        context['form'] = form
        return render(request, self.template_name, context)


    def get(self, request, *args, **kwargs):
        
        if 'object_type' in request.GET:
            object_type = request.GET.get('object_type')
            #print(f"GET request received with object_type: {object_type}")  # Debugging statement
            form_class = self.get_form_class(object_type)

            if form_class is None:
                print(f"Invalid object type: {object_type}")  # Debugging statement
                return HttpResponseBadRequest(f"Invalid object type: {object_type}")
            
            form = form_class()
            html = render_to_string('dynamic_form.html', {'form': form, 'object_type': object_type})
            return JsonResponse({'form': html})
        
        return super().get(request, *args, **kwargs)


    def get_form_class(self, object_type):
        #print(f"Retrieving form class for object_type: {object_type}")  # Debugging statement
        form_classes = {
            'butai': ButasSearchForm,
            'namai': NamasSearchForm,
            'patalpos': PatalposSearchForm,
            'sklypai': SklypaiSearchForm,
        }
        form_class = form_classes.get(object_type)

        if form_class is None:
            print(f"No form class found for object_type: {object_type}")  # Debugging statement

        return form_class


    def scrape_aruodas(self, data, object_type):
        """
        Webscraper gets this result: It may happen when you are opening a large number of pages in a short period of time, or when there are other
        indications that resembles automated bot behaviour. In such cases we will ask to verify that a real person is
        using the website.
        """

        base_url = f'https://www.aruodas.lt/{object_type}/'
        params = self.get_aruodas_url_params(data, object_type)

        # Prepare the full URL with parameters
        request = requests.Request('GET', base_url, params=params).prepare()
        full_url = request.url
        print(f"Full URL: {full_url}")  # Debugging statement

        response = requests.get(full_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        # print(f"Soup: {soup}")  # Debugging statement
        listings = []
        for listing in soup.select('.advert'):
            title = listing.select_one('.list-item-title').get_text(strip=True)
            price = listing.select_one('.list-item-price').get_text(strip=True)
            link = listing.select_one('.list-item-title a')['href']
            print(f"Found listing Title: {title}, Price: {price}, Link: {link}")  # Debugging statement
            listings.append({'title': title, 'price': price, 'link': link})
        return listings


    def get_aruodas_url_params(self, data, object_type):
        params = {
            'detailed_search': '1',
            'FAreaOverAllMin': data.get('area_from'),
            'FAreaOverAllMax': data.get('area_to'),
            'FRoomNumMin': data.get('room_count_from'),
            'FRoomNumMax': data.get('room_count_to'),
            'FPriceMin': data.get('price_from'),
            'FPriceMax': data.get('price_to'),
            'FHouseState': ','.join(data.get('equipment', [])),
            'FWarmSystem': ','.join(data.get('heating', [])),
            'FHouseType': ','.join(data.get('building_type', [])),
        }
        #print(f"Constructed URL params: {params}")  # Debugging statement
        return params







class EditSimilarObjectDataView(LoginRequiredMixin, UserRoleContextMixin, View):    
    """
    This view handles both the creation of new similar objects and the editing of existing similar objects.
    It includes forms for similar object data, location data, and additional data based on the object type.
    """

    model = Object
    model_order = Order
    model_user_meta = UserMeta
    model_similar_object = SimilarObject
    template_name = 'edit_object.html'
    success_url_name = 'modules.evaluator:edit_similar_object_decoration'
    login_url = 'core.uauth:login'
    redirect_field_name = 'next'

    form_class_location = ObjectLocationForm
    form_class_house = HouseForm
    form_class_land = LandForm
    form_class_apartament = ApartamentForm
    form_class_cottage = CottageForm
    form_class_similar_object = SimilarObjectForm



    def get_object(self):
        order_id = self.kwargs.get('order_id')
        pk = self.kwargs.get('pk')
        return get_object_or_404(self.model, id=pk, order__id=order_id)


    def get_additional_form(self, object_type, data=None):

        match object_type:
            case 'Namas':
                return self.form_class_house(data)
            
            case 'Sklypas':
                return self.form_class_land(data)
            
            case 'Butas':
                return self.form_class_apartament(data)
            
            case 'Kotedžas':
                return self.form_class_cottage(data)
            
            case 'Sodas':
                return self.form_class_house(data)
            
            case _:
                return None


    def get_context_data(self, **kwargs):
        """
        Prepares the context data for rendering the template.
        Retrieves the order, object, and client information, and initializes the forms.
        If the user is editing an existing similar object, the form fields are populated with the existing data.
        """
        context = {}
        order_id = self.kwargs.get('order_id')
        pk = self.kwargs.get('pk')
        order = get_object_or_404(self.model_order, id=order_id)
        obj = get_object_or_404(self.model, id=pk)
        client = order.client
        phone_number = self.model_user_meta.get_meta(client, 'phone_num')
        context['order'] = order
        context['object'] = obj
        context['client'] = client
        context['phone_number'] = phone_number
        context['order_id'] = order_id
        context['pk'] = pk
        context['is_similar_object'] = True
        context['is_evaluator'] = True
        context['show_progress_bar'] = False

        edit_id = self.request.GET.get('edit')

        if edit_id:
            similar_object = get_object_or_404(self.model_similar_object, id=edit_id)
            initial_data = {
                'price': similar_object.price,
                'link': similar_object.link,
                'description': similar_object.description
            }
            context['similar_object_form'] = self.form_class_similar_object(initial=initial_data)
            metadata_initial_data = {meta.key: meta.value for meta in similar_object.metadata.all()}
            context['location_form'] = self.form_class_location(initial=metadata_initial_data)
            context['additional_form'] = self.get_additional_form(obj.object_type, metadata_initial_data)
            context['similar_object_id'] = similar_object.id

        else:
            context['similar_object_form'] = self.form_class_similar_object()
            context['location_form'] = self.form_class_location()
            context['additional_form'] = self.get_additional_form(obj.object_type)
            context['similar_object_id'] = 0

        return context


    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return render(request, self.template_name, context)


    def post(self, request, *args, **kwargs):
        """
        Handles the POST request to create or update a similar object.
        Validates the forms and saves the data if valid.
        """

        context = self.get_context_data(**kwargs)
        location_form = self.form_class_location(request.POST)
        obj = context['object']

        # Determine the additional form based on the object type
        additional_form = self.get_additional_form(obj.object_type, request.POST)
        similar_object_form = self.form_class_similar_object(request.POST) if context['is_similar_object'] else None

        if location_form.is_valid() and (additional_form is None or additional_form.is_valid()) and (similar_object_form is None or similar_object_form.is_valid()):
            edit_id = request.POST.get('edit_id')
            
            if edit_id and edit_id != '0':
                similar_object = get_object_or_404(self.model_similar_object, id=edit_id)
                similar_object.price = similar_object_form.cleaned_data['price']
                similar_object.link = similar_object_form.cleaned_data['link']
                similar_object.description = similar_object_form.cleaned_data['description']

                similar_object.save()
                self.save_metadata(similar_object, location_form)

                if additional_form:
                    self.save_metadata(similar_object, additional_form)
            else:
                similar_object = self.model_similar_object(
                    original_object=context['object'],
                    price=similar_object_form.cleaned_data['price'],
                    link=similar_object_form.cleaned_data['link'],
                    description=similar_object_form.cleaned_data['description']
                )
                similar_object.save()
                self.save_metadata(similar_object, location_form)
                
                if additional_form:
                    self.save_metadata(similar_object, additional_form)

            return redirect(reverse_lazy(self.success_url_name, kwargs={'order_id': context['order_id'], 'pk': context['pk'], 'similar_object_id': similar_object.id}))
        
        return self.form_invalid(location_form, additional_form, similar_object_form)


    def form_invalid(self, location_form, additional_form, similar_object_form):
        context = self.get_context_data()
        context['location_form'] = location_form
        context['additional_form'] = additional_form
        context['similar_object_form'] = similar_object_form
        return self.render_to_response(context)


    def save_metadata(self, similar_object, form):
        for key, value in form.cleaned_data.items():
            SimilarObjectMetadata.objects.update_or_create(
                similar_object=similar_object,
                key=key,
                defaults={'value': value}
            )


            


class EditSimilarObjectDecorationView(LoginRequiredMixin, UserRoleContextMixin, View):
    """
    This view includes a form for decoration information and updates the metadata for the similar object.
    """

    model = Object
    model_order = Order
    model_user_meta = UserMeta
    template_name = 'edit_evaluation_deco_info.html'
    success_url_name = 'modules.evaluator:edit_similar_object_common_info'
    login_url = 'core.uauth:login'
    redirect_field_name = 'next'

    form_class_decoration = DecorationForm

    def get_object(self):
        order_id = self.kwargs.get('order_id')
        pk = self.kwargs.get('pk')
        return get_object_or_404(self.model, id=pk, order__id=order_id)


    def get_context_data(self, **kwargs):
        context = {}
        order_id = self.kwargs.get('order_id')
        pk = self.kwargs.get('pk')
        similar_object_id = self.kwargs.get('similar_object_id')
        order = get_object_or_404(self.model_order, id=order_id)
        obj = get_object_or_404(self.model, id=pk)
        similar_object = get_object_or_404(SimilarObject, id=similar_object_id)
        client = order.client
        phone_number = self.model_user_meta.get_meta(client, 'phone_num')
        context['order'] = order
        context['object'] = obj
        context['similar_object'] = similar_object
        context['client'] = client
        context['phone_number'] = phone_number
        context['order_id'] = order_id
        context['pk'] = pk
        context['similar_object_id'] = similar_object_id
        context['is_similar_object'] = True
        context['is_evaluator'] = True
        context['show_progress_bar'] = False


        initial_data = {meta.key: meta.value for meta in similar_object.metadata.all()}
        context['decoration_form'] = self.form_class_decoration(initial=initial_data)

        return context


    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return render(request, self.template_name, context)


    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        decoration_form = self.form_class_decoration(request.POST)

        if decoration_form.is_valid():
            similar_object = context['similar_object']
            self.save_metadata(similar_object, decoration_form)

            return redirect(reverse_lazy(self.success_url_name, kwargs={'order_id': context['order_id'], 'pk': context['pk'], 'similar_object_id': similar_object.id}))
        
        return self.form_invalid(decoration_form)


    def form_invalid(self, decoration_form):
        context = self.get_context_data()
        context['decoration_form'] = decoration_form
        return self.render_to_response(context)


    def save_metadata(self, similar_object, form):
        for key, value in form.cleaned_data.items():
            SimilarObjectMetadata.objects.update_or_create(
                similar_object=similar_object,
                key=key,
                defaults={'value': value}
            )


    
class EditSimilarObjectCommonInfoView(LoginRequiredMixin, UserRoleContextMixin, View):
    """
    This view includes a form for common information and updates the metadata for the similar object.
    """

    model = Object
    model_order = Order
    model_similar_object = SimilarObject
    model_usermeta = UserMeta
    template_name = 'edit_common_info.html'
    success_url_name = 'modules.evaluator:edit_similar_object_utility_info'
    login_url = 'core.uauth:login'
    redirect_field_name = 'next'

    form_class_common_info = CommonInformationForm

    def get_object(self):
        order_id = self.kwargs.get('order_id')
        pk = self.kwargs.get('pk')
        return get_object_or_404(self.model, id=pk, order__id=order_id)


    def get_context_data(self, **kwargs):
        context = {}
        order_id = self.kwargs.get('order_id')
        pk = self.kwargs.get('pk')
        similar_object_id = self.kwargs.get('similar_object_id')
        order = get_object_or_404(self.model_order, id=order_id)
        obj = get_object_or_404(self.model, id=pk)
        similar_object = get_object_or_404(self.model_similar_object, id=similar_object_id)
        client = order.client
        phone_number = self.model_usermeta.get_meta(client, 'phone_num')
        context['order'] = order
        context['object'] = obj
        context['similar_object'] = similar_object
        context['client'] = client
        context['phone_number'] = phone_number
        context['order_id'] = order_id
        context['pk'] = pk
        context['similar_object_id'] = similar_object_id
        context['is_similar_object'] = True
        context['is_evaluator'] = True
        context['show_progress_bar'] = False


        initial_data = {meta.key: meta.value for meta in similar_object.metadata.all()}
        context['common_info_form'] = self.form_class_common_info(initial=initial_data)

        return context


    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return render(request, self.template_name, context)


    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        common_info_form = self.form_class_common_info(request.POST)

        if common_info_form.is_valid():
            similar_object = context['similar_object']
            self.save_metadata(similar_object, common_info_form)

            return redirect(reverse_lazy(self.success_url_name, kwargs={'order_id': context['order_id'], 'pk': context['pk'], 'similar_object_id': similar_object.id}))
        
        return self.form_invalid(common_info_form)
    

    def form_invalid(self, common_info_form):
        context = self.get_context_data()
        context['common_info_form'] = common_info_form
        return self.render_to_response(context)

    def save_metadata(self, similar_object, form):
        for key, value in form.cleaned_data.items():
            SimilarObjectMetadata.objects.update_or_create(
                similar_object=similar_object,
                key=key,
                defaults={'value': value}
            )



class EditSimilarObjectUtilityInfoView(LoginRequiredMixin, UserRoleContextMixin, View):
    """
    This view includes a form for utility information and updates the metadata for the similar object.
    """

    model = Object
    model_order = Order
    model_similar_object = SimilarObject
    model_usermeta = UserMeta
    template_name = 'edit_utility_info.html'
    success_url_name = 'modules.evaluator:similar_object_list'
    login_url = 'core.uauth:login'
    redirect_field_name = 'next'

    form_class_utility = UtilityForm

    def get_object(self):
        order_id = self.kwargs.get('order_id')
        pk = self.kwargs.get('pk')
        return get_object_or_404(self.model, id=pk, order__id=order_id)


    def get_context_data(self, **kwargs):
        context = {}
        order_id = self.kwargs.get('order_id')
        pk = self.kwargs.get('pk')
        similar_object_id = self.kwargs.get('similar_object_id')
        order = get_object_or_404(self.model_order, id=order_id)
        obj = get_object_or_404(self.model, id=pk)
        similar_object = get_object_or_404(self.model_similar_object, id=similar_object_id)
        client = order.client
        phone_number = self.model_usermeta.get_meta(client, 'phone_num')
        context['order'] = order
        context['object'] = obj
        context['similar_object'] = similar_object
        context['client'] = client
        context['phone_number'] = phone_number
        context['order_id'] = order_id
        context['pk'] = pk
        context['is_similar_object'] = True
        context['is_evaluator'] = True
        context['similar_object_id'] = similar_object_id
        context['show_progress_bar'] = False


        initial_data = {meta.key: meta.value for meta in similar_object.metadata.all()}
        context['utility_form'] = self.form_class_utility(initial=initial_data)

        return context


    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return render(request, self.template_name, context)


    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        utility_form = self.form_class_utility(request.POST)

        if utility_form.is_valid():
            similar_object = context['similar_object']
            self.save_metadata(similar_object, utility_form)

            return redirect(reverse_lazy(self.success_url_name, kwargs={'order_id': context['order_id'], 'pk': context['pk']}))
        
        return self.form_invalid(utility_form)


    def form_invalid(self, utility_form):
        context = self.get_context_data()
        context['utility_form'] = utility_form
        return self.render_to_response(context)


    def save_metadata(self, similar_object, form):
        for key, value in form.cleaned_data.items():
            SimilarObjectMetadata.objects.update_or_create(
                similar_object=similar_object,
                key=key,
                defaults={'value': value}
            )



class SimilarObjectResultsView(LoginRequiredMixin, UserRoleContextMixin, TemplateView):
    """
    This view retrieves and displays the search results for similar objects based on the search criteria.
    """

    model_usermeta = UserMeta
    template_name = 'similar_object_results.html'
    login_url = 'core.uauth:login'
    redirect_field_name = 'next'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_id = self.kwargs.get('order_id')
        pk = self.kwargs.get('pk')
        order = get_object_or_404(Order, id=order_id)
        obj = get_object_or_404(Object, id=pk)
        client = order.client
        phone_number = self.model_usermeta.get_meta(client, 'phone_num')
        context['order'] = order
        context['object'] = obj
        context['client'] = client
        context['phone_number'] = phone_number
        context['order_id'] = order_id
        context['pk'] = pk
        context['show_progress_bar'] = True
        context['is_evaluator'] = True
        context['current_step'] = 5
        context['total_steps'] = 8
        return context




class SimilarObjectListView(LoginRequiredMixin, UserRoleContextMixin, View):
    """
    This view retrieves and displays the list of similar objects associated with a specific order and object.
    """
    
    template_name = 'similar_object_list.html'
    login_url = 'core.uauth:login'
    redirect_field_name = 'next'
    model_order = Order
    model_object = Object
    model_similar_object = SimilarObject
    model_usermeta = UserMeta

    def get(self, request, *args, **kwargs):
        order_id = self.kwargs.get('order_id')
        pk = self.kwargs.get('pk')
        order = get_object_or_404(self.model_order, id=order_id)
        obj = get_object_or_404(self.model_object, id=pk)
        similar_objects = self.model_similar_object.objects.filter(original_object=obj)

        for similar_object in similar_objects:
            metadata = {meta.key: meta.value for meta in similar_object.metadata.all()}
            similar_object.living_size = metadata.get('living_size', 'N/A')
            similar_object.room_count = metadata.get('room_count', 'N/A')
            similar_object.price = similar_object.price

        client = order.client
        phone_number = self.model_usermeta.get_meta(client, 'phone_num')

        context = {
            'order': order,
            'object': obj,
            'similar_objects': similar_objects,
            'order_id': order_id,
            'pk': pk,
            'show_progress_bar': True,
            'is_evaluator': True,
            'current_step': 5,
            'total_steps': 8,
            'client': client,
            'phone_number': phone_number
        }
        return render(request, self.template_name, context)