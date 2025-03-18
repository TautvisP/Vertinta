import decimal
from django.shortcuts import render, redirect, get_object_or_404
from modules.orders.enums import ObjectImages
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView, ListView, View, UpdateView, DetailView
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from modules.orders.enums import MUNICIPALITY_CHOICES, STATUS_CHOICES, PRIORITY_CHOICES
from modules.orders.models import Order, Object, ObjectMeta
from modules.orders.forms import HouseForm, LandForm, ApartamentForm, CottageForm, ObjectLocationForm, DecorationForm, UtilityForm, CommonInformationForm, OrderStatusForm, GarageForm, ShedForm, GazeboForm
from core.uauth.models import User, UserMeta
from django.db.models import Count, Q, F
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from shared.mixins.mixins import UserRoleContextMixin
from django.contrib import messages
from django.contrib.auth import get_user_model
import datetime


# Global message variables
SUCCESS_MESSAGE = _("Profilis sėkmingai atnaujintas!")
MISTAKE_MESSAGE = _("Pataisykite klaidas.")
NO_PERMISSION_MESSAGE = _("Neturite leidimo pasiekti šį puslapį.")


def index(request):
    return render(request, 'orders/index.html')

def test_view(request):
    return render(request, 'shared/header.html')


class LandingView(LoginRequiredMixin, UserPassesTestMixin, UserRoleContextMixin, ListView):
    """
    Displays a list of object images for the landing page.
    Requires the user to be logged in and have the appropriate role.
    """

    template_name = "object_select.html"
    login_url = 'core.uauth:login'
    redirect_field_name = 'next'

    def test_func(self):
        return not (self.request.user.groups.filter(name='Agency').exists() or self.request.user.groups.filter(name='Evaluator').exists())

    def handle_no_permission(self):
        messages.error(self.request, NO_PERMISSION_MESSAGE)
        return redirect('core.uauth:login')


    def get_queryset(self):
        return ObjectImages

    def get_selected_obj_type(self, request):

        if 'selected_obj_type' in self.request.session:
            object_type = request.session['selected_obj_type']

        if object_type is not None:
            return object_type
        
        return None


    def post(self, request):
        selected_obj_type = request.POST.get('object_type')
        if selected_obj_type:
            request.session['selected_obj_type'] = selected_obj_type
            # Clear any existing data from previous attempts
            for key in ['location_data', 'additional_data', 'decoration_data', 'common_info_data', 'utility_data']:
                if key in request.session:
                    del request.session[key]
            return redirect('modules.orders:order_creation_step')
        
        # If no object type selected, show an error
        messages.error(request, _('Please select an object type'))
        return redirect('modules.orders:selection')


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('Užsisakykite NT vertinimą')
        return context


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
        # Get selected object type from session if it exists (set in LandingView)
        selected_obj_type = request.session.get('selected_obj_type', '')
        
        if not selected_obj_type:
            # If no object type is selected, redirect back to selection
            return redirect('modules.orders:selection')
        
        location_data = request.session.get('location_data', {})
        additional_data = request.session.get('additional_data', {})
        
        # Initialize location form with session data if it exists
        location_form = self.form_location(initial=location_data)
        
        # Prepare context with minimal data
        context = {
            'location_form': location_form,
            'selected_obj_type': selected_obj_type,
            'is_creation': True,
            'show_progress_bar': True,
            'current_step': 1,
            'total_steps': 5
        }
        
        # Add the corresponding form based on the object type
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
        # Get the selected object type from session, not from POST
        # This ensures we're using the object type selected in the previous step
        selected_obj_type = request.session.get('selected_obj_type')
        
        if not selected_obj_type:
            # If no object type, redirect back to selection
            return redirect('modules.orders:selection')
        
        # Process location form
        location_form = self.form_location(request.POST)
        
        # Initialize additional form based on object type
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
        
        # Validate both forms
        location_valid = location_form.is_valid()
        additional_valid = additional_form.is_valid() if additional_form else True
        
        # Both forms need to be valid to proceed
        if location_valid and additional_valid:
            # Store data in session - convert Decimal to str for JSON serialization
            location_data = location_form.cleaned_data.copy()
            location_data = self.convert_decimals_in_dict(location_data)
            request.session['location_data'] = location_data
            
            if additional_form:
                additional_data = additional_form.cleaned_data.copy()
                additional_data = self.convert_decimals_in_dict(additional_data)
                request.session['additional_data'] = additional_data
            
            # Redirect to decoration step
            return redirect('modules.orders:order_decoration_step')
        
        # If forms are not valid, prepare context with entered data and errors
        context = {
            'location_form': location_form,
            'selected_obj_type': selected_obj_type,
            'is_creation': True,
            'show_progress_bar': True,
            'current_step': 1,
            'total_steps': 5
        }
        
        # Add the additional form with errors
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
        # Check if we have the necessary session data from previous step
        if not request.session.get('selected_obj_type') or not request.session.get('location_data'):
            # If essential data is missing, redirect back to the first step
            return redirect('modules.orders:order_creation_step')
        
        # Get decoration data from session if it exists
        decoration_data = request.session.get('decoration_data', {})
        
        # Create the form with initial data
        decoration_form = self.form_class(initial=decoration_data)
        
        context = {
            'decoration_form': decoration_form,
            'is_creation': True,
            'show_progress_bar': True,
            'current_step': 2,
            'total_steps': 5
        }
        return render(request, self.template_name, context)
    
    def post(self, request):
        # Process the form
        form = self.form_class(request.POST)

        if form.is_valid():
            # Store form data in session with proper conversion
            decoration_data = form.cleaned_data.copy()
            # Since DecorationForm doesn't have dates, we can use the existing function
            decoration_data = self.convert_serializable_in_dict(decoration_data)
            request.session['decoration_data'] = decoration_data

            # Redirect to the next step - common information
            return redirect('modules.orders:order_common_info_step')

        # If form is not valid, show errors
        context = {
            'decoration_form': form,
            'is_creation': True,
            'show_progress_bar': True,
            'current_step': 2,
            'total_steps': 5
        }
        return render(request, self.template_name, context)
    
    @staticmethod
    def convert_serializable_in_dict(data_dict):
        """Convert non-JSON-serializable objects (Decimal, date) to strings in a dictionary."""
        import datetime
        result = data_dict.copy()
        for key, value in result.items():
            if isinstance(value, decimal.Decimal):
                result[key] = str(value)
            elif isinstance(value, datetime.date):
                result[key] = value.isoformat()  # Convert date to ISO format string
        return result



class ObjectCommonInfoStepView(LoginRequiredMixin, UserRoleContextMixin, View):
    """
    Third step of creating an order. This view displays the common information form.
    """
    template_name = 'order_common_info_step.html'  # Use the new template
    form_class = CommonInformationForm
    
    @staticmethod
    def convert_serializable_in_dict(data_dict):
        """Convert non-JSON-serializable objects (Decimal, date) to strings in a dictionary."""
        import datetime
        result = data_dict.copy()
        for key, value in result.items():
            if isinstance(value, decimal.Decimal):
                result[key] = str(value)
            elif isinstance(value, datetime.date):
                result[key] = value.isoformat()  # Convert date to ISO format string
        return result
    
    def get(self, request):
        # Check if we have the necessary session data from previous steps
        if not request.session.get('selected_obj_type') or not request.session.get('location_data') or not request.session.get('decoration_data'):
            # If essential data is missing, redirect back to the appropriate step
            if not request.session.get('decoration_data'):
                return redirect('modules.orders:order_decoration_step')
            return redirect('modules.orders:order_creation_step')
        
        # Get common info data from session if it exists
        common_info_data = request.session.get('common_info_data', {})
        
        # Create the form with initial data
        common_info_form = self.form_class(initial=common_info_data)
        
        context = {
            'common_info_form': common_info_form,
            'is_creation': True,
            'show_progress_bar': True,
            'current_step': 3,
            'total_steps': 5
        }
        return render(request, self.template_name, context)
    
    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            # Store form data in session with proper conversion for dates and decimals
            common_info_data = form.cleaned_data.copy()
            common_info_data = self.convert_serializable_in_dict(common_info_data)
            request.session['common_info_data'] = common_info_data

            # Redirect to the next step - utility
            return redirect('modules.orders:order_utility_step')

        # If form is not valid, show errors
        context = {
            'common_info_form': form,
            'is_creation': True,
            'show_progress_bar': True,
            'current_step': 3,
            'total_steps': 5
        }
        return render(request, self.template_name, context)



class ObjectUtilityStepView(LoginRequiredMixin, UserRoleContextMixin, View):
    """
    Fourth step of creating an order. This view displays the utility form.
    """
    template_name = 'order_utility_step.html'  # Use our new template
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
        # Check if we have the necessary session data from previous steps
        if not request.session.get('selected_obj_type') or not request.session.get('location_data') or \
           not request.session.get('decoration_data') or not request.session.get('common_info_data'):
            # If essential data is missing, redirect back to the appropriate step
            if not request.session.get('common_info_data'):
                return redirect('modules.orders:order_common_info_step')
            elif not request.session.get('decoration_data'):
                return redirect('modules.orders:order_decoration_step')
            return redirect('modules.orders:order_creation_step')
        
        # Get utility data from session if it exists
        utility_data = request.session.get('utility_data', {})
        
        # Create the form with initial data
        utility_form = self.form_class(initial=utility_data)
        
        context = {
            'utility_form': utility_form,
            'is_creation': True,
            'show_progress_bar': True,
            'current_step': 4,
            'total_steps': 5
        }
        return render(request, self.template_name, context)
    
    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            # Store form data in session
            utility_data = form.cleaned_data.copy()
            utility_data = self.convert_decimals_in_dict(utility_data)
            request.session['utility_data'] = utility_data

            # For object type Namas/Kotedžas, redirect to additional buildings
            selected_obj_type = request.session.get('selected_obj_type')
            if selected_obj_type in ['Namas', 'Kotedžas']:
                # Create the object first and pass its ID to the additional buildings step
                obj = self.create_object(request)
                return redirect('modules.orders:additional_buildings', object_id=obj.id)

            # Otherwise, create just the object (not the order)
            obj = self.create_object(request)

            # Don't clear session data yet
            # We'll need it for the agency selection

            # Redirect to agency selection
            return redirect('modules.orders:select_agency', object_id=obj.id)

        # If form is not valid, show errors
        context = {
            'utility_form': form,
            'is_creation': True,
            'show_progress_bar': True,
            'current_step': 4,
            'total_steps': 5
        }
        return render(request, self.template_name, context)
    
    def create_object(self, request):
        # Get all the data from session
        location_data = request.session.get('location_data', {})
        decoration_data = request.session.get('decoration_data', {})
        common_info_data = request.session.get('common_info_data', {})
        utility_data = request.session.get('utility_data', {})
        selected_obj_type = request.session.get('selected_obj_type', '')
        additional_data = request.session.get('additional_data', {})

        # Create the object
        obj = Object.objects.create(
            object_type=selected_obj_type,
            latitude=location_data.get('latitude'),
            longitude=location_data.get('longitude')
        )

        # Save all other data as ObjectMeta
        all_metadata = {}
        all_metadata.update(location_data)
        all_metadata.update(decoration_data)
        all_metadata.update(common_info_data)
        all_metadata.update(utility_data)
        all_metadata.update(additional_data)

        # Remove fields already stored directly on the Object model
        for field in ['object_type', 'latitude', 'longitude']:
            if field in all_metadata:
                del all_metadata[field]

        # Save all metadata
        for key, value in all_metadata.items():
            if value is not None:  # Only save non-null values
                ObjectMeta.objects.create(ev_object=obj, meta_key=key, meta_value=str(value))

        # Store the object ID in the session for the agency selection view
        request.session['pending_object_id'] = obj.id

        return obj
    
    def clear_session_data(self, request):
        # Clear all session data related to order creation
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


    

class OrderListView(LoginRequiredMixin, UserRoleContextMixin, UserPassesTestMixin, ListView):
    """
    Displays a list of orders for the current user.
    Requires the user to be logged in and have the appropriate role.
    Includes filtering capabilities for municipality, status, and priority.
    """
        
    model = Order
    template_name = "order_list.html"
    context_object_name = "orders"
    login_url = 'core.uauth:login'
    redirect_field_name = 'next'

    def test_func(self):
        return not self.request.user.groups.filter(name='Evaluator').exists()

    def handle_no_permission(self):
        messages.error(self.request, NO_PERMISSION_MESSAGE)
        return redirect('core.uauth:login')

    def get_queryset(self):
        user = self.request.user    

        if user.groups.filter(name='Agency').exists():
            queryset = self.model.objects.filter(agency=user)
        else:
            queryset = self.model.objects.filter(client=user)
            
        municipality = self.request.GET.get('municipality')
        if municipality:
            object_ids = ObjectMeta.objects.filter(
                meta_key='municipality', 
                meta_value=municipality
            ).values_list('ev_object_id', flat=True)
            
            queryset = queryset.filter(object_id__in=object_ids)    

        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)   

        priority = self.request.GET.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('Užsakymų sąrašas')
        context['user_is_agency'] = self.request.user.groups.filter(name='Agency').exists()
        
        context['municipality_choices'] = MUNICIPALITY_CHOICES
        context['status_choices'] = STATUS_CHOICES
        context['priority_choices'] = PRIORITY_CHOICES
        
        evaluator_phones = {}
        for order in context['orders']:
            if order.evaluator and order.evaluator.id not in evaluator_phones:
                phone = UserMeta.get_meta(order.evaluator, 'phone_num')
                evaluator_phones[order.evaluator.id] = phone
        context['evaluator_phones'] = evaluator_phones
    
        
        return context




class EvaluatorOrderListView(LoginRequiredMixin, UserRoleContextMixin, UserPassesTestMixin, ListView):
    """
    Displays a list of orders for the evaluator.
    Requires the user to be logged in and have the appropriate role.
    """

    model = Order
    template_name = "evaluator_order_list.html"
    context_object_name = "orders"
    login_url = 'core.uauth:login'
    redirect_field_name = 'next'

    def test_func(self):
        user = self.request.user
        evaluator_id = self.kwargs.get('id')
        
        # If viewing a specific evaluator's orders
        if evaluator_id:

            # For agency users: Check if the evaluator belongs to their agency
            if user.groups.filter(name='Agency').exists():
                try:
                    evaluator = get_user_model().objects.get(id=evaluator_id)
                    # Check if this evaluator belongs to the current agency
                    return evaluator.agency == user
                
                except get_user_model().DoesNotExist:
                    return False
                
            # Evaluators can only view their own orders
            elif user.groups.filter(name='Evaluator').exists():
                return str(user.id) == str(evaluator_id)
            
            return False
        
        else:
            # If no specific ID, just check if user is either an evaluator or agency
            return user.groups.filter(name__in=['Evaluator', 'Agency']).exists()


    def handle_no_permission(self):
        messages.error(self.request, _("Jūs neturite teisės peržiūrėti šio vertintojo užsakymų."))
        
        # Redirect evaluators to their own orders page
        if self.request.user.groups.filter(name='Evaluator').exists():
            return redirect('modules.orders:evaluator_order_list')
        
        # Redirect agency users to evaluator list
        elif self.request.user.groups.filter(name='Agency').exists():
            return redirect('modules.agency:evaluator_list')
            
        return redirect('core.uauth:login')

    def get_queryset(self):
        user = self.request.user
        evaluator_id = self.kwargs.get('id')

        if evaluator_id:
            queryset = self.model.objects.filter(evaluator_id=evaluator_id)
        else:
            queryset = self.model.objects.filter(evaluator=user)

        municipality = self.request.GET.get('municipality')
        if municipality:
            queryset = queryset.filter(object__objectmeta__meta_key='municipality', object__objectmeta__meta_value=municipality)

        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        priority = self.request.GET.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)

        return queryset


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['municipality_choices'] = MUNICIPALITY_CHOICES
        context['status_choices'] = STATUS_CHOICES
        context['priority_choices'] = PRIORITY_CHOICES
        context['is_agency'] = self.request.user.groups.filter(name='Agency').exists()
        context['is_evaluator'] = self.request.user.groups.filter(name='Evaluator').exists()
        return context




class OrderDeleteView(LoginRequiredMixin, View):
    """
    Handles the deletion of an order and its metadata.
    Only allows deletion if the user is the creator of the order.
    """
    
    def post(self, request, *args, **kwargs):
        order_id = kwargs.get('pk')
        order = get_object_or_404(Order, id=order_id)

        # Check if the user is the creator of the order
        if order.client != request.user:
            messages.error(request, "Neturite teisių ištrinti šį įrašą.")
            return redirect('modules.orders:order_list')

        obj = order.object

        # Delete associated metadata and object
        ObjectMeta.objects.filter(ev_object=obj).delete()
        obj.delete()
        order.delete()

        messages.success(request, "Užsakymas ištrintas sėkmingai.")
        return HttpResponseRedirect(reverse_lazy('modules.orders:order_list'))




class ObjectUpdateView(UserRoleContextMixin, UserPassesTestMixin, UpdateView):
    """
    Handles the updating of object data.
    Includes forms for location, decoration, utility, and common information.
    """

    model = Object
    template_name = "user_edit_order.html"
    success_url = reverse_lazy('modules.orders:order_list')
    fields = []

    form_object_location = ObjectLocationForm
    form_decoration = DecorationForm
    form_utility = UtilityForm
    form_common_info = CommonInformationForm
    form_house = HouseForm
    form_land = LandForm
    form_apartament = ApartamentForm
    form_cottage = CottageForm

    def test_func(self):
        return not (self.request.user.groups.filter(name='Agency').exists() or self.request.user.groups.filter(name='Evaluator').exists())

    def handle_no_permission(self):
        messages.error(self.request, NO_PERMISSION_MESSAGE)
        return redirect('core.uauth:login')

    def get_initial_data(self, obj):
        initial_data = {}
        meta_data = ObjectMeta.objects.filter(ev_object=obj)

        for meta in meta_data:
            initial_data[meta.meta_key] = meta.meta_value

        return initial_data


    def get_context_data(self, **kwargs):
        """
        Prepares the context data for rendering the template.
        Initializes the forms based on the object's metadata.
        """
                
        context = super().get_context_data(**kwargs)
        obj = self.get_object()
        initial_data = self.get_initial_data(obj)
        context['location_form'] = self.form_object_location(initial=initial_data)
        context['decoration_form'] = self.form_decoration(initial=initial_data)
        context['utility_form'] = self.form_utility(initial=initial_data)
        context['common_info_form'] = self.form_common_info(initial=initial_data)

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

        return context


    def post(self, request, *args, **kwargs):
        """
        Handles the POST request to update the object data.
        Validates the forms and saves the data if valid.
        """
                
        obj = self.get_object()
        self.object = obj
        initial_data = self.get_initial_data(obj)
        location_form = self.form_object_location(request.POST, initial=initial_data)
        decoration_form = self.form_decoration(request.POST, initial=initial_data)
        utility_form = self.form_utility(request.POST, initial=initial_data)
        common_info_form = self.form_common_info(request.POST, initial=initial_data)

        match obj.object_type:
            case 'Namas':
                additional_form = self.form_house(request.POST, initial=initial_data)

            case 'Sklypas':
                additional_form = self.form_land(request.POST, initial=initial_data)

            case 'Butas':
                additional_form = self.form_apartament(request.POST, initial=initial_data)

            case 'Kotedžas':
                additional_form = self.form_cottage(request.POST, initial=initial_data)

            case 'Sodas':
                additional_form = self.form_house(request.POST, initial=initial_data)

            case _:
                additional_form = None

        if location_form.is_valid() and decoration_form.is_valid() and utility_form.is_valid() and common_info_form.is_valid() and (additional_form is None or additional_form.is_valid()):
            self.save_form_data(obj, location_form.cleaned_data)
            self.save_form_data(obj, decoration_form.cleaned_data)
            self.save_form_data(obj, utility_form.cleaned_data)
            self.save_form_data(obj, common_info_form.cleaned_data)
            
            if additional_form:
                self.save_form_data(obj, additional_form.cleaned_data)
            #return redirect(reverse_lazy('modules.orders:edit_additional_buildings', kwargs={'pk': obj.pk}))
            return redirect(self.success_url)
        
        return self.form_invalid(location_form, decoration_form, utility_form, common_info_form, additional_form)


    def form_invalid(self, location_form, decoration_form, utility_form, common_info_form, additional_form=None, garage_form=None, shed_form=None, gazebo_form=None):
        context = self.get_context_data()
        context.update({
            'location_form': location_form,
            'decoration_form': decoration_form,
            'utility_form': utility_form,
            'common_info_form': common_info_form,
        })

        if additional_form:
            context['additional_form'] = additional_form

        return self.render_to_response(context)


    def save_form_data(self, obj, cleaned_data):
        for key, value in cleaned_data.items():
            self.model.save_meta(obj, key, value)




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




class AgencySelectionView(LoginRequiredMixin, UserPassesTestMixin, UserRoleContextMixin, ListView):
    """
    Displays a list of agencies for the user to select from.
    Requires the user to be logged in.
    """

    model = User
    model_order = Order
    model_user_meta = UserMeta
    template_name = 'agency_selection.html'
    context_object_name = 'agencies'
    login_url = 'core.uauth:login'
    redirect_field_name = 'next'

    def test_func(self):
        return not (self.request.user.groups.filter(name='Agency').exists() or self.request.user.groups.filter(name='Evaluator').exists())

    def handle_no_permission(self):
        messages.error(self.request, NO_PERMISSION_MESSAGE)
        return redirect('core.uauth:login')
    

    def get_queryset(self):
        return self.model.objects.filter(groups__name='Agency').annotate(
            evaluator_count=Count('evaluators', filter=Q(evaluators__agency_id=F('id')))
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Check if we have an order_id or object_id in the URL
        order_id = self.kwargs.get('order_id')
        object_id = self.kwargs.get('object_id')
        
        # Handle both possible URL parameter scenarios
        if order_id:
            context['order_id'] = order_id
        elif object_id:
            # If we only have object_id but no order_id, pass the object_id
            context['object_id'] = object_id
        
        agencies = self.get_queryset()
        agency_data = []
        ongoing_status = STATUS_CHOICES[2][0]
        completed_status = STATUS_CHOICES[3][0]
        for agency in agencies:
            evaluators = agency.evaluators.all()
            ongoing_orders_count = sum(evaluator.evaluator_orders.filter(status=ongoing_status).count() for evaluator in evaluators)
            completed_orders_count = sum(evaluator.evaluator_orders.filter(status=completed_status).count() for evaluator in evaluators)
            agency_data.append({
                'id': agency.id,
                'name': self.model_user_meta.get_meta(agency, 'agency_name'),
                'date_joined': agency.date_joined,
                'evaluator_count': evaluators.count(),  # Use actual count instead of agency.evaluator_count
                'ongoing_orders': ongoing_orders_count,
                'completed_orders': completed_orders_count,
                'evaluation_starting_price': self.model_user_meta.get_meta(agency, 'evaluation_starting_price'),
            })
        context['agency_data'] = agency_data
        context['title'] = _('Select an Agency')
        return context

    def post(self, request, *args, **kwargs):
        selected_agency_id = request.POST.get('selected_agency_id')
        if selected_agency_id:
            try:
                selected_agency = self.model.objects.get(id=selected_agency_id, groups__name='Agency')
                
                # Check if we have an order_id or object_id
                order_id = self.kwargs.get('order_id')
                object_id = self.kwargs.get('object_id')
                
                if order_id:
                    # Update an existing order
                    order = get_object_or_404(Order, id=order_id)
                    order.agency = selected_agency
                    order.save()
                    
                elif object_id:
                    # Create a new order for this object
                    obj = get_object_or_404(Object, id=object_id)
                    order = Order.objects.create(
                        client=request.user,
                        object=obj,
                        agency=selected_agency,
                        status='Naujas'  # Default status for new orders
                    )
                    
                    # Select the appraiser with the least amount of orders
                    appraisers = self.model.objects.filter(groups__name='Evaluator', agency=selected_agency)
                    if appraisers.exists():
                        appraiser_with_least_orders = min(appraisers, key=lambda appraiser: appraiser.evaluator_orders.count())
                        # Associate the order with the selected appraiser
                        order.evaluator = appraiser_with_least_orders
                        order.save()
                
                # Clear session data
                for key in ['selected_obj_type', 'location_data', 'decoration_data', 
                            'common_info_data', 'utility_data', 'additional_data', 'pending_object_id']:
                    if key in request.session:
                        del request.session[key]
                
                messages.success(request, _("Order created successfully!"))
                return redirect('modules.orders:order_list')
            
            except Exception as e:
                messages.error(request, _("Error creating order: ") + str(e))
                
        return self.get(request, *args, **kwargs)
    




class ViewObjectDataView(LoginRequiredMixin, UserRoleContextMixin, DetailView):
    """
    This view displays the object data without editing capabilities.
    Only the associated users (client, evaluator, and agency) can view it.
    """
    model = Object
    template_name = 'view_object_data.html'
    context_object_name = 'object'
    user_meta = ObjectMeta

    def dispatch(self, request, *args, **kwargs):
        order_id = self.kwargs.get('order_id')
        order = get_object_or_404(Order, id=order_id)
        user = request.user

        # Check if the user is the client, evaluator, or agency associated with the order
        if not (order.client == user or order.evaluator == user or (order.evaluator and order.evaluator.agency == user)):
            messages.error(request, "Neturite teisių peržiūrėti šios informacijos.")
            return redirect('modules.orders:order_list')

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_id = self.kwargs.get('order_id')
        order = get_object_or_404(Order, id=order_id)
        obj = order.object
        meta_data = ObjectMeta.objects.filter(ev_object=obj)
        meta_dict = {meta.meta_key: meta.meta_value for meta in meta_data}
        context['meta_data'] = meta_dict
        context['order'] = order
        context['order_id'] = order_id
        context['pk'] = self.kwargs['pk']
        context['show_progress_bar'] = False
        context['is_evaluator'] = self.request.user.groups.filter(name='Evaluator').exists()
        return context

    def get_success_url(self):
        if self.request.user.groups.filter(name='Evaluator').exists():
            return reverse_lazy('modules.evaluator:evaluator_order_list')
        else:
            return reverse_lazy('modules.orders:order_list')




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
        # Get the object being edited
        pk = kwargs.get('pk')
        order_id = kwargs.get('order_id')
        
        obj = get_object_or_404(Object, pk=pk)
        
        # Prepare context with object data
        context = {
            'is_editing': True,
            'pk': pk,
            'object': obj,
            'selected_obj_type': obj.object_type,
            'show_progress_bar': True,
            'current_step': 1,
            'total_steps': 5
        }
        
        # Add order to context if provided
        if order_id:
            order = get_object_or_404(Order, id=order_id)
            context['order'] = order
            context['order_id'] = order_id
        
        # Get initial data from object metadata
        initial_data = {}
        
        # Add direct fields
        if hasattr(obj, 'latitude') and obj.latitude:
            initial_data['latitude'] = obj.latitude
        if hasattr(obj, 'longitude') and obj.longitude:
            initial_data['longitude'] = obj.longitude
        
        # Add metadata fields
        meta_data = ObjectMeta.objects.filter(ev_object=obj)
        for meta in meta_data:
            initial_data[meta.meta_key] = meta.meta_value
        
        # Initialize location form with object data
        context['location_form'] = self.form_location(initial=initial_data)
        
        # Initialize additional form based on object type
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
        # Get the object being edited
        print("editing")
        pk = kwargs.get('pk')
        order_id = kwargs.get('order_id')
        
        obj = get_object_or_404(Object, pk=pk)
        
        # Process submitted forms
        location_form = self.form_location(request.POST)
        
        # Initialize additional form based on object type
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
        
        # Validate both forms
        location_valid = location_form.is_valid()
        additional_valid = additional_form and additional_form.is_valid()
        
        if location_valid and additional_valid:
            # Save location form data to object
            # Handle direct fields first
            if hasattr(obj, 'latitude') and 'latitude' in location_form.cleaned_data:
                obj.latitude = location_form.cleaned_data['latitude']
            if hasattr(obj, 'longitude') and 'longitude' in location_form.cleaned_data:
                obj.longitude = location_form.cleaned_data['longitude']
            obj.save()
            
            # Handle all other location fields as metadata
            location_data = location_form.cleaned_data.copy()
            
            # Remove direct fields from metadata
            if 'latitude' in location_data:
                del location_data['latitude']
            if 'longitude' in location_data:
                del location_data['longitude']
                
            # Save location metadata
            for key, value in location_data.items():
                ObjectMeta.objects.update_or_create(
                    ev_object=obj,
                    meta_key=key,
                    defaults={'meta_value': str(value) if value is not None else ''}
                )
                
            # Save additional form data as metadata
            if additional_form:
                for key, value in additional_form.cleaned_data.items():
                    ObjectMeta.objects.update_or_create(
                        ev_object=obj,
                        meta_key=key,
                        defaults={'meta_value': str(value) if value is not None else ''}
                    )
            
            # Redirect to next step in editing flow
            return redirect('modules.orders:edit_decoration_step', pk=pk)
        
        # If forms are not valid, redisplay with errors
        context = {
            'is_editing': True,
            'pk': pk,
            'object': obj,
            'location_form': location_form,
            'selected_obj_type': obj.object_type,
            'show_progress_bar': True,
            'current_step': 1,
            'total_steps': 5
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
        # Get object being edited
        pk = kwargs.get('pk')
        order_id = kwargs.get('order_id')
        
        obj = get_object_or_404(Object, pk=pk)
        
        # Prepare context
        context = {
            'is_editing': True,
            'pk': pk,
            'object': obj,
            'show_progress_bar': True,
            'current_step': 2,
            'total_steps': 5
        }
        
        # Add order to context if provided
        if order_id:
            order = get_object_or_404(Order, id=order_id)
            context['order'] = order
            context['order_id'] = order_id
            
        # Get initial data from object metadata
        initial_data = {}
        meta_data = ObjectMeta.objects.filter(ev_object=obj)
        for meta in meta_data:
            initial_data[meta.meta_key] = meta.meta_value
            
        # Initialize form with object data
        context['decoration_form'] = self.form_class(initial=initial_data)
        
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        # Get object being edited
        pk = kwargs.get('pk')
        order_id = kwargs.get('order_id')
        
        obj = get_object_or_404(Object, pk=pk)
        
        # Process the form
        form = self.form_class(request.POST)
        
        if form.is_valid():
            # Save form data as metadata
            for key, value in form.cleaned_data.items():
                ObjectMeta.objects.update_or_create(
                    ev_object=obj,
                    meta_key=key,
                    defaults={'meta_value': str(value) if value is not None else ''}
                )
                
            # Redirect to the next step
            return redirect('modules.orders:edit_common_info_step', pk=pk)
                
        # If form is not valid, redisplay with errors
        context = {
            'is_editing': True,
            'pk': pk,
            'object': obj,
            'decoration_form': form,
            'show_progress_bar': True,
            'current_step': 2,
            'total_steps': 5
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
        # Get object being edited
        pk = kwargs.get('pk')
        order_id = kwargs.get('order_id')
        
        obj = get_object_or_404(Object, pk=pk)
        
        # Prepare context
        context = {
            'is_editing': True,
            'pk': pk,
            'object': obj,
            'show_progress_bar': True,
            'current_step': 3,
            'total_steps': 5
        }
        
        # Add order to context if provided
        if order_id:
            order = get_object_or_404(Order, id=order_id)
            context['order'] = order
            context['order_id'] = order_id
            
        # Get initial data from object metadata
        initial_data = {}
        meta_data = ObjectMeta.objects.filter(ev_object=obj)
        for meta in meta_data:
            initial_data[meta.meta_key] = meta.meta_value
            
        # Initialize form with object data
        context['common_info_form'] = self.form_class(initial=initial_data)
        
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        # Get object being edited
        pk = kwargs.get('pk')
        order_id = kwargs.get('order_id')
        
        obj = get_object_or_404(Object, pk=pk)
        
        # Process the form
        form = self.form_class(request.POST)
        
        if form.is_valid():
            # Save form data as metadata
            for key, value in form.cleaned_data.items():
                # Convert date objects to ISO format strings
                if isinstance(value, datetime.date):
                    value = value.isoformat()
                
                ObjectMeta.objects.update_or_create(
                    ev_object=obj,
                    meta_key=key,
                    defaults={'meta_value': str(value) if value is not None else ''}
                )
                
            # Redirect to the next step
            return redirect('modules.orders:edit_utility_step', pk=pk)
                
        # If form is not valid, redisplay with errors
        context = {
            'is_editing': True,
            'pk': pk,
            'object': obj,
            'common_info_form': form,
            'show_progress_bar': True,
            'current_step': 3,
            'total_steps': 5
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
        # Get object being edited
        pk = kwargs.get('pk')
        order_id = kwargs.get('order_id')
        
        obj = get_object_or_404(Object, pk=pk)
        
        # Prepare context
        context = {
            'is_editing': True,
            'pk': pk,
            'object': obj,
            'show_progress_bar': True,
            'current_step': 4,
            'total_steps': 5
        }
        
        # Add order to context if provided
        if order_id:
            order = get_object_or_404(Order, id=order_id)
            context['order'] = order
            context['order_id'] = order_id
            
        # Get initial data from object metadata
        initial_data = {}
        meta_data = ObjectMeta.objects.filter(ev_object=obj)
        for meta in meta_data:
            initial_data[meta.meta_key] = meta.meta_value
            
        # Initialize form with object data
        context['utility_form'] = self.form_class(initial=initial_data)
        
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        # Get object being edited
        pk = kwargs.get('pk')
        order_id = kwargs.get('order_id')
        
        obj = get_object_or_404(Object, pk=pk)
        
        # Process the form
        form = self.form_class(request.POST)
        
        if form.is_valid():
            # Save form data as metadata
            for key, value in form.cleaned_data.items():
                # Convert non-serializable values to strings
                if isinstance(value, decimal.Decimal):
                    value = str(value)
                elif isinstance(value, datetime.date):
                    value = value.isoformat()
                
                ObjectMeta.objects.update_or_create(
                    ev_object=obj,
                    meta_key=key,
                    defaults={'meta_value': str(value) if value is not None else ''}
                )
            
            # Redirect to the next step or final page
            messages.success(request, _("Object updated successfully!"))
            return redirect('modules.orders:order_list')
                
        # If form is not valid, redisplay with errors
        context = {
            'is_editing': True,
            'pk': pk,
            'object': obj,
            'utility_form': form,
            'show_progress_bar': True,
            'current_step': 4,
            'total_steps': 5
        }
        
        if order_id:
            order = get_object_or_404(Order, id=order_id)
            context['order'] = order
            context['order_id'] = order_id
            
        return render(request, self.template_name, context)