import decimal
import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, View
from django.utils.translation import gettext as _
from modules.orders.models import Order, Object, ObjectMeta
from modules.orders.forms import HouseForm, LandForm, ApartamentForm, CottageForm, ObjectLocationForm, DecorationForm, UtilityForm, CommonInformationForm, GarageForm, ShedForm, GazeboForm
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from shared.mixins.mixins import UserRoleContextMixin
from django.contrib import messages

NO_PERMISSION_MESSAGE = _("Neturite leidimo pasiekti šį puslapį.")


class OrderCreationStepView(LoginRequiredMixin, UserRoleContextMixin, View):
    """
    First step of creating an order. This view displays the location form
    and object type selection, along with an additional form based on the selected type.
    """
    template_name = 'order_creation_step.html'
    form_location = ObjectLocationForm
    form_house = HouseForm
    form_land = LandForm
    form_apartament = ApartamentForm
    form_cottage = CottageForm
    

    def get(self, request):
        selected_obj_type = request.session.get('selected_obj_type', '')
        
        if not selected_obj_type:

            return redirect('modules.orders:selection')
        
        location_data = request.session.get('location_data', {})
        additional_data = request.session.get('additional_data', {})
        location_form = self.form_location(initial=location_data)
        
        context = {
            'location_form': location_form,
            'selected_obj_type': selected_obj_type,
            'is_creation': True,
        }
        
        match selected_obj_type:
            case 'Namas':
                context['additional_form'] = self.form_house(initial=additional_data)
            case 'Sklypas':
                context['additional_form'] = self.form_land(initial=additional_data)
            case 'Butas':
                context['additional_form'] = self.form_apartament(initial=additional_data)
            case 'Kotedžas':
                context['additional_form'] = self.form_cottage(initial=additional_data)
            case 'Sodas':
                context['additional_form'] = self.form_house(initial=additional_data)
        
        return render(request, self.template_name, context)
    

    @staticmethod
    def convert_decimals_in_dict(data_dict):
        """Convert Decimal objects to strings in a dictionary."""
        result = data_dict.copy()

        for key, value in result.items():

            if isinstance(value, decimal.Decimal):
                result[key] = str(value)

        return result
    

    def post(self, request):
        selected_obj_type = request.session.get('selected_obj_type')
        
        if not selected_obj_type:

            return redirect('modules.orders:selection')
        
        location_form = self.form_location(request.POST)
        
        additional_form = None

        match selected_obj_type:
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
        additional_valid = additional_form.is_valid() if additional_form else True
        
        if location_valid and additional_valid:

            location_data = location_form.cleaned_data.copy()
            location_data = self.convert_decimals_in_dict(location_data)
            request.session['location_data'] = location_data
            
            if additional_form:

                additional_data = additional_form.cleaned_data.copy()
                additional_data = self.convert_decimals_in_dict(additional_data)
                request.session['additional_data'] = additional_data
            
            return redirect('modules.orders:order_decoration_step')
        
        context = {
            'location_form': location_form,
            'selected_obj_type': selected_obj_type,
            'is_creation': True,
        }
        
        if additional_form:
            context['additional_form'] = additional_form
        
        return render(request, self.template_name, context)





class OrderDecorationStepView(LoginRequiredMixin, UserRoleContextMixin, View):
    """
    Second step of creating an order. This view displays the decoration form.
    """
    template_name = 'order_decoration_step.html'
    form_class = DecorationForm
    
    def get(self, request):

        if not request.session.get('selected_obj_type') or not request.session.get('location_data'):

            return redirect('modules.orders:order_creation_step')
        
        decoration_data = request.session.get('decoration_data', {})
        decoration_form = self.form_class(initial=decoration_data)
        context = {
            'decoration_form': decoration_form,
            'is_creation': True,
        }

        return render(request, self.template_name, context)
    

    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            decoration_data = form.cleaned_data.copy()
            decoration_data = self.convert_serializable_in_dict(decoration_data)
            request.session['decoration_data'] = decoration_data

            return redirect('modules.orders:order_common_info_step')

        context = {
            'decoration_form': form,
            'is_creation': True,
        }

        return render(request, self.template_name, context)
    

    @staticmethod
    def convert_serializable_in_dict(data_dict):
        """Convert non-JSON-serializable objects (Decimal, date) to strings in a dictionary."""
        result = data_dict.copy()
        
        for key, value in result.items():

            if isinstance(value, decimal.Decimal):
                result[key] = str(value)

            elif isinstance(value, datetime.date):
                result[key] = value.isoformat()

        return result




class ObjectCommonInfoStepView(LoginRequiredMixin, UserRoleContextMixin, View):
    """
    Third step of creating an order. This view displays the common information form.
    """
    template_name = 'order_common_info_step.html'
    form_class = CommonInformationForm
    
    @staticmethod
    def convert_serializable_in_dict(data_dict):
        """Convert non-JSON-serializable objects (Decimal, date) to strings in a dictionary."""
        result = data_dict.copy()

        for key, value in result.items():

            if isinstance(value, decimal.Decimal):
                result[key] = str(value)

            elif isinstance(value, datetime.date):
                result[key] = value.isoformat()

        return result
    
    def get(self, request):

        if not request.session.get('selected_obj_type') or not request.session.get('location_data') or not request.session.get('decoration_data'):

            if not request.session.get('decoration_data'):

                return redirect('modules.orders:order_decoration_step')
            
            return redirect('modules.orders:order_creation_step')
        
        common_info_data = request.session.get('common_info_data', {})
        common_info_form = self.form_class(initial=common_info_data)
        context = {
            'common_info_form': common_info_form,
            'is_creation': True,
        }

        return render(request, self.template_name, context)
    

    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():

            common_info_data = form.cleaned_data.copy()
            common_info_data = self.convert_serializable_in_dict(common_info_data)
            request.session['common_info_data'] = common_info_data

            return redirect('modules.orders:order_utility_step')

        context = {
            'common_info_form': form,
            'is_creation': True,
        }

        return render(request, self.template_name, context)




class ObjectUtilityStepView(LoginRequiredMixin, UserRoleContextMixin, View):
    """
    Fourth step of creating an order. This view displays the utility form.
    """
    template_name = 'order_utility_step.html'
    form_class = UtilityForm
    
    @staticmethod
    def convert_decimals_in_dict(data_dict):
        """Convert Decimal objects to strings in a dictionary."""
        result = data_dict.copy()

        for key, value in result.items():

            if isinstance(value, decimal.Decimal):
                result[key] = str(value)

        return result
    
    def get(self, request):

        if not request.session.get('selected_obj_type') or not request.session.get('location_data') or \
           not request.session.get('decoration_data') or not request.session.get('common_info_data'):
            
            if not request.session.get('common_info_data'):
                return redirect('modules.orders:order_common_info_step')
            
            elif not request.session.get('decoration_data'):
                return redirect('modules.orders:order_decoration_step')
            
            return redirect('modules.orders:order_creation_step')
        
        utility_data = request.session.get('utility_data', {})
        utility_form = self.form_class(initial=utility_data)
        context = {
            'utility_form': utility_form,
            'is_creation': True,
        }
        return render(request, self.template_name, context)
    

    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():

            utility_data = form.cleaned_data.copy()
            utility_data = self.convert_decimals_in_dict(utility_data)
            request.session['utility_data'] = utility_data
            selected_obj_type = request.session.get('selected_obj_type')

            if selected_obj_type in ['Namas', 'Kotedžas']:

                obj = self.create_object(request)
                return redirect('modules.orders:additional_buildings', object_id=obj.id)

            obj = self.create_object(request)

            return redirect('modules.orders:select_agency', object_id=obj.id)

        context = {
            'utility_form': form,
            'is_creation': True,
        }

        return render(request, self.template_name, context)
    

    def create_object(self, request):
        location_data = request.session.get('location_data', {})
        decoration_data = request.session.get('decoration_data', {})
        common_info_data = request.session.get('common_info_data', {})
        utility_data = request.session.get('utility_data', {})
        selected_obj_type = request.session.get('selected_obj_type', '')
        additional_data = request.session.get('additional_data', {})

        obj = Object.objects.create(
            object_type=selected_obj_type,
            latitude=location_data.get('latitude'),
            longitude=location_data.get('longitude')
        )

        all_metadata = {}
        all_metadata.update(location_data)
        all_metadata.update(decoration_data)
        all_metadata.update(common_info_data)
        all_metadata.update(utility_data)
        all_metadata.update(additional_data)

        for field in ['object_type', 'latitude', 'longitude']:

            if field in all_metadata:
                del all_metadata[field]

        for key, value in all_metadata.items():

            if value is not None:
                ObjectMeta.objects.create(ev_object=obj, meta_key=key, meta_value=str(value))

        request.session['pending_object_id'] = obj.id

        return obj
    
    
    def clear_session_data(self, request):
        keys_to_clear = ['selected_obj_type', 'location_data', 'decoration_data', 
                         'common_info_data', 'utility_data', 'additional_data']
        
        for key in keys_to_clear:

            if key in request.session:
                del request.session[key]




class AdditionalBuildingsView(LoginRequiredMixin, UserRoleContextMixin, UserPassesTestMixin, TemplateView):
    """
    Handles the additional buildings step in the order creation process.
    Includes forms for garage, shed, and gazebo data.
    """
    template_name = 'additional_buildings.html'
    login_url = 'core.uauth:login'
    redirect_field_name = 'next'
    success_url = 'modules.orders:select_agency'

    form_garage = GarageForm
    form_shed = ShedForm
    form_gazebo = GazeboForm

    def test_func(self):
        return not (self.request.user.groups.filter(name='Agency').exists() or self.request.user.groups.filter(name='Evaluator').exists())

    def handle_no_permission(self):
        messages.error(self.request, NO_PERMISSION_MESSAGE)
        return redirect('core.uauth:login')
    

    def get_forms(self):
        object_id = self.kwargs.get('object_id')
        obj = get_object_or_404(Object, id=object_id)
        garage_data = ObjectMeta.objects.filter(ev_object=obj, meta_key__startswith='garage_')
        shed_data = ObjectMeta.objects.filter(ev_object=obj, meta_key__startswith='shed_')
        gazebo_data = ObjectMeta.objects.filter(ev_object=obj, meta_key__startswith='gazebo_')
        
        forms = {
            'garage_form': self.form_garage(prefix='garage'),
            'shed_form': self.form_shed(prefix='shed'),
            'gazebo_form': self.form_gazebo(prefix='gazebo'),
        }

        if garage_data.exists():
            garage_initial = {meta.meta_key: meta.meta_value for meta in garage_data}
            forms['garage_form'] = self.form_garage(initial=garage_initial, prefix='garage')

        if shed_data.exists():
            shed_initial = {meta.meta_key: meta.meta_value for meta in shed_data}
            forms['shed_form'] = self.form_shed(initial=shed_initial, prefix='shed')

        if gazebo_data.exists():
            gazebo_initial = {meta.meta_key: meta.meta_value for meta in gazebo_data}
            forms['gazebo_form'] = self.form_gazebo(initial=gazebo_initial, prefix='gazebo')

        return forms


    def dispatch(self, request, *args, **kwargs):
        object_id = self.kwargs.get('object_id')
        obj = get_object_or_404(Object, id=object_id)

        # Check if additional buildings data has already been entered
        garage_data = ObjectMeta.objects.filter(ev_object=obj, meta_key__startswith='garage_')
        shed_data = ObjectMeta.objects.filter(ev_object=obj, meta_key__startswith='shed_')
        gazebo_data = ObjectMeta.objects.filter(ev_object=obj, meta_key__startswith='gazebo_')

        if garage_data.exists() or shed_data.exists() or gazebo_data.exists():
            order = Order.objects.filter(object=obj).first()
            return redirect('modules.orders:select_agency', order_id=order.id)

        return super().dispatch(request, *args, **kwargs)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.get_forms())
        context['show_progress_bar'] = False
        object_id = self.kwargs.get('object_id')
        obj = get_object_or_404(Object, id=object_id)
        context['object'] = obj
        context['object_id'] = object_id

        # Try to get the order, but don't fail if it doesn't exist yet
        order = Order.objects.filter(object=obj).first()
        if order:
            context['order'] = order
            context['order_id'] = order.id
        else:
            # No order yet, this is part of the creation flow
            context['order'] = None
            context['order_id'] = None

        context['is_evaluator'] = self.request.user.groups.filter(name='Evaluator').exists()
        context['has_additional_buildings'] = obj.has_additional_buildings
        return context


    def post(self, request, *args, **kwargs):
        forms = self.get_forms()
        all_valid = True

        if 'garage_submit' in request.POST:
            form_instance = self.form_garage(request.POST, prefix='garage')

            if form_instance.is_valid():
                self.save_form_data(form_instance.cleaned_data)

            else:
                forms['garage_form'] = form_instance
                all_valid = False

        elif 'shed_submit' in request.POST:
            form_instance = self.form_shed(request.POST, prefix='shed')

            if form_instance.is_valid():
                self.save_form_data(form_instance.cleaned_data)

            else:
                forms['shed_form'] = form_instance
                all_valid = False

        elif 'gazebo_submit' in request.POST:
            form_instance = self.form_gazebo(request.POST, prefix='gazebo')

            if form_instance.is_valid():
                self.save_form_data(form_instance.cleaned_data)

            else:
                forms['gazebo_form'] = form_instance
                all_valid = False

        if all_valid:
            object_id = self.kwargs.get('object_id')
            obj = get_object_or_404(Object, id=object_id)
            # Check if there's an order, if not, this is part of creation flow
            order = Order.objects.filter(object=obj).first()
            if not order:
                # We're in the creation flow, go to agency selection
                return redirect('modules.orders:select_agency', object_id=object_id)
            else:
                # We have an order, go to edit order
                return redirect('modules.orders:select_agency', order_id=order.id)

        return self.form_invalid(forms)


    def form_invalid(self, forms):
        context = self.get_context_data()
        context.update(forms)
        return self.render_to_response(context)


    def save_form_data(self, cleaned_data):
        object_id = self.kwargs.get('object_id')
        obj = get_object_or_404(Object, id=object_id)
        for key, value in cleaned_data.items():
            ObjectMeta.objects.create(ev_object=obj, meta_key=key, meta_value=value)