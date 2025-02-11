"""
This view contains the first two steps of the multi-step evaluation process.
Contains 4 views that are used to edit the object data.
And contains a view for editing additional building data.
"""
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import DetailView
from django.views.generic.edit import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from shared.mixins.mixins import UserRoleContextMixin
from modules.orders.models import Object, ObjectMeta, Order
from modules.orders.forms import ObjectLocationForm, HouseForm, LandForm, ApartamentForm, CottageForm, DecorationForm, CommonInformationForm, UtilityForm, GarageForm, ShedForm, GazeboForm
from modules.evaluator.forms import EvaluationForm
from django.utils.translation import gettext as _


# Global context variables
TOTAL_STEPS = 8
SHOW_PROGRESS_BAR = True



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
        initial_data = {
            'municipality': obj.municipality,
            'street': obj.street,
            'house_no': obj.house_no,
            'latitude': obj.latitude,
            'longitude': obj.longitude,
        }
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


        order_id = self.kwargs.get('order_id')
        order = get_object_or_404(Order, id=order_id)
        context['order'] = order
        context['order_id'] = order_id
        context['pk'] = self.kwargs['pk']
        context['current_step'] = 1
        context['total_steps'] = TOTAL_STEPS
        context['show_progress_bar'] = SHOW_PROGRESS_BAR
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
            if key in ['latitude', 'longitude']:
                setattr(obj, key, value)
            else:
                self.model.save_meta(obj, key, value)
        obj.save()




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
        order_id = self.kwargs.get('order_id')
        order = get_object_or_404(Order, id=order_id)
        context['order'] = order
        context['order_id'] = order_id
        context['pk'] = self.kwargs['pk']
        context['current_step'] = 1
        context['total_steps'] = TOTAL_STEPS
        context['show_progress_bar'] = SHOW_PROGRESS_BAR
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
        order_id = self.kwargs.get('order_id')
        order = get_object_or_404(Order, id=order_id)
        context['order'] = order
        context['order_id'] = order_id
        context['pk'] = self.kwargs['pk']
        context['current_step'] = 1
        context['total_steps'] = TOTAL_STEPS 
        context['show_progress_bar'] = SHOW_PROGRESS_BAR
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
        order_id = self.kwargs.get('order_id')
        order = get_object_or_404(Order, id=order_id)
        context['order'] = order
        context['order_id'] = order_id
        context['pk'] = self.kwargs['pk']
        context['current_step'] = 1
        context['total_steps'] = TOTAL_STEPS
        context['show_progress_bar'] = SHOW_PROGRESS_BAR
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
        context_flags = {}

        if garage_data.exists():
            garage_initial = {meta.meta_key: meta.meta_value for meta in garage_data}
            forms['garage_form'] = self.form_class_garage(initial=garage_initial, prefix='garage')
            context_flags['show_garage_form'] = True

        else:
            forms['garage_form'] = self.form_class_garage(prefix='garage')
            context_flags['show_garage_form'] = False

        if shed_data.exists():
            shed_initial = {meta.meta_key: meta.meta_value for meta in shed_data}
            forms['shed_form'] = self.form_class_shed(initial=shed_initial, prefix='shed')
            context_flags['show_shed_form'] = True

        else:
            forms['shed_form'] = self.form_class_shed(prefix='shed')
            context_flags['show_shed_form'] = False

        if gazebo_data.exists():
            gazebo_initial = {meta.meta_key: meta.meta_value for meta in gazebo_data}
            forms['gazebo_form'] = self.form_class_gazebo(initial=gazebo_initial, prefix='gazebo')
            context_flags['show_gazebo_form'] = True

        else:
            forms['gazebo_form'] = self.form_class_gazebo(prefix='gazebo')
            context_flags['show_gazebo_form'] = False

        return forms, context_flags


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        forms, context_flags = self.get_forms()
        context.update(forms)
        context.update(context_flags)
        context['pk'] = self.kwargs['pk']
        context['show_progress_bar'] = True
        order_id = self.kwargs.get('order_id')
        order = get_object_or_404(Order, id=order_id)
        context['order'] = order
        context['order_id'] = order_id
        context['is_evaluator'] = True
        context['current_step'] = 2
        context['total_steps'] = 8

        # Check for additional buildings
        garage_buildings = ObjectMeta.objects.filter(ev_object=self.get_object(), meta_key__startswith='garage_')
        shed_buildings = ObjectMeta.objects.filter(ev_object=self.get_object(), meta_key__startswith='shed_')
        gazebo_buildings = ObjectMeta.objects.filter(ev_object=self.get_object(), meta_key__startswith='gazebo_')

        if not (garage_buildings.exists() or shed_buildings.exists() or gazebo_buildings.exists()):
            self.template_name = "additional_buildings.html"

        return context


    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        self.object = obj
        print("POST request received")

        garage_form = self.form_class_garage(request.POST, prefix='garage')
        shed_form = self.form_class_shed(request.POST, prefix='shed')
        gazebo_form = self.form_class_gazebo(request.POST, prefix='gazebo')

        if garage_form.is_valid():
            self.save_form_data(obj, garage_form.cleaned_data)
            print("Garage form data saved:", garage_form.cleaned_data)
            return redirect(self.get_success_url())
        
        elif shed_form.is_valid():
            self.save_form_data(obj, shed_form.cleaned_data)
            print("Shed form data saved:", shed_form.cleaned_data)
            return redirect(self.get_success_url())
        
        elif gazebo_form.is_valid():
            self.save_form_data(obj, gazebo_form.cleaned_data)
            print("Gazebo form data saved:", gazebo_form.cleaned_data)
            return redirect(self.get_success_url())

        forms = {
            'garage_form': garage_form,
            'shed_form': shed_form,
            'gazebo_form': gazebo_form,
        }
        return self.form_invalid(forms)


    def form_invalid(self, forms):
        context = self.get_context_data()
        context.update(forms)
        return self.render_to_response(context)


    def save_form_data(self, obj, cleaned_data):
        
        for key, value in cleaned_data.items():
            print(f"Saving {key}: {value}")
            self.model_meta.objects.update_or_create(ev_object=obj, meta_key=key, defaults={'meta_value': value})