import decimal
import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, UpdateView
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from modules.orders.enums import PRIORITY_CHOICES, ObjectImages
from modules.orders.models import Order, Object, ObjectMeta
from modules.orders.forms import HouseForm, LandForm, ApartamentForm, CottageForm, ObjectLocationForm, DecorationForm, UtilityForm, CommonInformationForm, OrderStatusForm, GarageForm, ShedForm, GazeboForm
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from shared.mixins.mixins import UserRoleContextMixin
from django.contrib import messages


NO_PERMISSION_MESSAGE = _("Neturite leidimo pasiekti šį puslapį.")


class EditObjectStepView(LoginRequiredMixin, UserRoleContextMixin, View):
    """
    Edit step view for existing objects. This view reuses the order creation templates
    but populates them with existing object data for editing.
    """
    template_name = 'order_creation_step.html'
    form_location = ObjectLocationForm
    form_house = HouseForm
    form_land = LandForm
    form_apartament = ApartamentForm
    form_cottage = CottageForm
    
    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        order_id = kwargs.get('order_id')
        
        obj = get_object_or_404(Object, pk=pk)
        
        context = {
            'is_editing': True,
            'pk': pk,
            'object': obj,
            'selected_obj_type': obj.object_type,
        }
        
        if order_id:
            order = get_object_or_404(Order, id=order_id)
            context['order'] = order
            context['order_id'] = order_id
        
        initial_data = {}
        
        if hasattr(obj, 'latitude') and obj.latitude:
            initial_data['latitude'] = obj.latitude

        if hasattr(obj, 'longitude') and obj.longitude:
            initial_data['longitude'] = obj.longitude
        
        meta_data = ObjectMeta.objects.filter(ev_object=obj)

        for meta in meta_data:
            initial_data[meta.meta_key] = meta.meta_value
        
        context['location_form'] = self.form_location(initial=initial_data)
        
        match obj.object_type:
            case 'Namas':
                context['additional_form'] = self.form_house(initial=initial_data)
            case 'Sklypas':
                context['additional_form'] = self.form_land(initial=initial_data)
            case 'Butas':
                context['additional_form'] = self.form_apartament(initial=initial_data)
            case 'Kotedžas':
                context['additional_form'] = self.form_cottage(initial=initial_data)
            case 'Sodas':
                context['additional_form'] = self.form_house(initial=initial_data)
        
        return render(request, self.template_name, context)


    def post(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        order_id = kwargs.get('order_id')
        obj = get_object_or_404(Object, pk=pk)
        location_form = self.form_location(request.POST)
        
        additional_form = None
        match obj.object_type:
            case 'Namas':
                additional_form = self.form_house(request.POST)
            case 'Sklypas':
                additional_form = self.form_land(request.POST)
            case 'Butas':
                additional_form = self.form_apartament(request.POST)
            case 'Kotedžas':
                additional_form = self.form_cottage(request.POST)
            case 'Sodas':
                additional_form = self.form_house(request.POST)
        
        location_valid = location_form.is_valid()
        additional_valid = additional_form and additional_form.is_valid()
        
        if location_valid and additional_valid:

            if hasattr(obj, 'latitude') and 'latitude' in location_form.cleaned_data:
                obj.latitude = location_form.cleaned_data['latitude']

            if hasattr(obj, 'longitude') and 'longitude' in location_form.cleaned_data:
                obj.longitude = location_form.cleaned_data['longitude']

            obj.save()
            
            location_data = location_form.cleaned_data.copy()
            
            if 'latitude' in location_data:
                del location_data['latitude']

            if 'longitude' in location_data:
                del location_data['longitude']
                
            for key, value in location_data.items():
                ObjectMeta.objects.update_or_create(
                    ev_object=obj,
                    meta_key=key,
                    defaults={'meta_value': str(value) if value is not None else ''}
                )
                
            if additional_form:

                for key, value in additional_form.cleaned_data.items():
                    ObjectMeta.objects.update_or_create(
                        ev_object=obj,
                        meta_key=key,
                        defaults={'meta_value': str(value) if value is not None else ''}
                    )
            
            return redirect('modules.orders:edit_decoration_step', pk=pk)
        
        context = {
            'is_editing': True,
            'pk': pk,
            'object': obj,
            'location_form': location_form,
            'selected_obj_type': obj.object_type,
        }
        
        if order_id:
            order = get_object_or_404(Order, id=order_id)
            context['order'] = order
            context['order_id'] = order_id
            
        if additional_form:
            context['additional_form'] = additional_form
            
        return render(request, self.template_name, context)




class EditObjectDecorationStepView(LoginRequiredMixin, UserRoleContextMixin, View):
    """
    Second step for editing an object: Decoration information.
    """
    template_name = 'order_decoration_step.html'
    form_class = DecorationForm
    
    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        order_id = kwargs.get('order_id')
        obj = get_object_or_404(Object, pk=pk)
        
        context = {
            'is_editing': True,
            'pk': pk,
            'object': obj,
        }
        
        if order_id:
            order = get_object_or_404(Order, id=order_id)
            context['order'] = order
            context['order_id'] = order_id
            
        initial_data = {}
        meta_data = ObjectMeta.objects.filter(ev_object=obj)

        for meta in meta_data:
            initial_data[meta.meta_key] = meta.meta_value
            
        context['decoration_form'] = self.form_class(initial=initial_data)
        
        return render(request, self.template_name, context)
    

    def post(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        order_id = kwargs.get('order_id')
        obj = get_object_or_404(Object, pk=pk)
        form = self.form_class(request.POST)
        
        if form.is_valid():

            for key, value in form.cleaned_data.items():
                ObjectMeta.objects.update_or_create(
                    ev_object=obj,
                    meta_key=key,
                    defaults={'meta_value': str(value) if value is not None else ''}
                )
                
            return redirect('modules.orders:edit_common_info_step', pk=pk)
                
        context = {
            'is_editing': True,
            'pk': pk,
            'object': obj,
            'decoration_form': form,
        }
        
        if order_id:
            order = get_object_or_404(Order, id=order_id)
            context['order'] = order
            context['order_id'] = order_id
            
        return render(request, self.template_name, context)
    



class EditObjectCommonInfoStepView(LoginRequiredMixin, UserRoleContextMixin, View):
    """
    Third step for editing an object: Common information.
    This view populates and processes the common information form for an existing object.
    """
    template_name = 'order_common_info_step.html'
    form_class = CommonInformationForm
    
    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        order_id = kwargs.get('order_id')
        obj = get_object_or_404(Object, pk=pk)
        
        context = {
            'is_editing': True,
            'pk': pk,
            'object': obj,
        }
        
        if order_id:
            order = get_object_or_404(Order, id=order_id)
            context['order'] = order
            context['order_id'] = order_id
            
        initial_data = {}
        meta_data = ObjectMeta.objects.filter(ev_object=obj)

        for meta in meta_data:
            initial_data[meta.meta_key] = meta.meta_value
            
        context['common_info_form'] = self.form_class(initial=initial_data)
        
        return render(request, self.template_name, context)
    

    def post(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        order_id = kwargs.get('order_id')
        obj = get_object_or_404(Object, pk=pk)
        form = self.form_class(request.POST)
        
        if form.is_valid():

            for key, value in form.cleaned_data.items():

                if isinstance(value, datetime.date):
                    value = value.isoformat()
                
                ObjectMeta.objects.update_or_create(
                    ev_object=obj,
                    meta_key=key,
                    defaults={'meta_value': str(value) if value is not None else ''}
                )
                
            return redirect('modules.orders:edit_utility_step', pk=pk)
                
        context = {
            'is_editing': True,
            'pk': pk,
            'object': obj,
            'common_info_form': form,
        }
        
        if order_id:
            order = get_object_or_404(Order, id=order_id)
            context['order'] = order
            context['order_id'] = order_id
            
        return render(request, self.template_name, context)
    



class EditObjectUtilityStepView(LoginRequiredMixin, UserRoleContextMixin, View):
    """
    Fourth step for editing an object: Utility information.
    This view populates and processes the utility form for an existing object.
    """
    template_name = 'order_utility_step.html'
    form_class = UtilityForm
    
    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        order_id = kwargs.get('order_id')
        obj = get_object_or_404(Object, pk=pk)
        
        context = {
            'is_editing': True,
            'pk': pk,
            'object': obj,
        }
        
        if order_id:
            order = get_object_or_404(Order, id=order_id)
            context['order'] = order
            context['order_id'] = order_id
            
        initial_data = {}
        meta_data = ObjectMeta.objects.filter(ev_object=obj)

        for meta in meta_data:
            initial_data[meta.meta_key] = meta.meta_value
            
        context['utility_form'] = self.form_class(initial=initial_data)
        
        return render(request, self.template_name, context)
    

    def post(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        order_id = kwargs.get('order_id')
        obj = get_object_or_404(Object, pk=pk)
        form = self.form_class(request.POST)
        
        if form.is_valid():

            for key, value in form.cleaned_data.items():

                if isinstance(value, decimal.Decimal):
                    value = str(value)

                elif isinstance(value, datetime.date):
                    value = value.isoformat()
                
                ObjectMeta.objects.update_or_create(
                    ev_object=obj,
                    meta_key=key,
                    defaults={'meta_value': str(value) if value is not None else ''}
                )
            
            messages.success(request, _("Object updated successfully!"))
            return redirect('modules.orders:order_list')
                
        context = {
            'is_editing': True,
            'pk': pk,
            'object': obj,
            'utility_form': form,
        }
        
        if order_id:
            order = get_object_or_404(Order, id=order_id)
            context['order'] = order
            context['order_id'] = order_id
            
        return render(request, self.template_name, context)




class EditOrderStatusPriorityView(LoginRequiredMixin, UserRoleContextMixin, UserPassesTestMixin, UpdateView):
    """
    View to edit the status and priority of an order.
    Requires the user to be logged in.
    """
    model = Order
    form_class = OrderStatusForm
    template_name = 'edit_order_status_priority.html'
    context_object_name = 'order'

    def test_func(self):
        return self.request.user.groups.filter(name='Agency').exists() or self.request.user.groups.filter(name='Evaluator').exists()

    def handle_no_permission(self):
        messages.error(self.request, NO_PERMISSION_MESSAGE)
        return redirect('core.uauth:login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['priority_choices'] = PRIORITY_CHOICES
        return context

    def get_success_url(self):
        return reverse_lazy('modules.orders:evaluator_order_list')    




class EditAdditionalBuildingsView(LoginRequiredMixin, UserRoleContextMixin, UserPassesTestMixin, UpdateView):
    """
    Handles the editing of additional buildings associated with an object.
    Includes forms for garage, shed, and gazebo data.
    """
        
    model = Object
    model_meta = ObjectMeta
    template_name = "edit_additional_buildings.html"
    success_url = reverse_lazy('modules.orders:order_list')
    fields = []

    form_garage = GarageForm
    form_shed = ShedForm
    form_gazebo = GazeboForm

    def test_func(self):
        return not (self.request.user.groups.filter(name='Agency').exists() or self.request.user.groups.filter(name='Evaluator').exists())


    def handle_no_permission(self):
        messages.error(self.request, NO_PERMISSION_MESSAGE)
        return redirect('core.uauth:login')
    

    def get_object(self, queryset=None):
        return get_object_or_404(self.model, pk=self.kwargs['pk'])


    def get_forms(self):
        obj = self.get_object()
        garage_data = self.model_meta.objects.filter(ev_object=obj, meta_key__startswith='garage_')
        shed_data = self.model_meta.objects.filter(ev_object=obj, meta_key__startswith='shed_')
        gazebo_data = self.model_meta.objects.filter(ev_object=obj, meta_key__startswith='gazebo_')
        
        forms = {}
        context_flags = {}

        if garage_data.exists():
            garage_initial = {meta.meta_key: meta.meta_value for meta in garage_data}
            forms['garage_form'] = self.form_garage(initial=garage_initial, prefix='garage')
            context_flags['show_garage_form'] = True

        else:
            forms['garage_form'] = self.form_garage(prefix='garage')
            context_flags['show_garage_form'] = False

        if shed_data.exists():
            shed_initial = {meta.meta_key: meta.meta_value for meta in shed_data}
            forms['shed_form'] = self.form_shed(initial=shed_initial, prefix='shed')
            context_flags['show_shed_form'] = True

        else:
            forms['shed_form'] = self.form_shed(prefix='shed')
            context_flags['show_shed_form'] = False

        if gazebo_data.exists():
            gazebo_initial = {meta.meta_key: meta.meta_value for meta in gazebo_data}
            forms['gazebo_form'] = self.form_gazebo(initial=gazebo_initial, prefix='gazebo')
            context_flags['show_gazebo_form'] = True

        else:
            forms['gazebo_form'] = self.form_gazebo(prefix='gazebo')
            context_flags['show_gazebo_form'] = False

        return forms, context_flags


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        forms, context_flags = self.get_forms()
        context.update(forms)
        context.update(context_flags)
        context['show_progress_bar'] = False
        context['is_evaluator'] = False 
        return context


    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        self.object = obj

        garage_form = self.form_garage(request.POST, prefix='garage')
        shed_form = self.form_shed(request.POST, prefix='shed')
        gazebo_form = self.form_gazebo(request.POST, prefix='gazebo')

        if garage_form.is_valid():
            self.save_form_data(obj, garage_form.cleaned_data)
            print("Garage form data saved:", garage_form.cleaned_data)
            return redirect(self.success_url)

        elif shed_form.is_valid():
            self.save_form_data(obj, shed_form.cleaned_data)
            print("Shed form data saved:", shed_form.cleaned_data)
            return redirect(self.success_url)

        elif gazebo_form.is_valid():
            self.save_form_data(obj, gazebo_form.cleaned_data)
            print("Gazebo form data saved:", gazebo_form.cleaned_data)
            return redirect(self.success_url)

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
