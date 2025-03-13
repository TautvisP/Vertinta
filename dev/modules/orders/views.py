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


    def post(self, request, **kwargs):
        selected_obj_type = request.POST.get('object_type')
        request.session['selected_obj_type'] = selected_obj_type
        return HttpResponseRedirect(reverse_lazy('modules.orders:order_first_step'))


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('Užsisakykite NT vertinimą')
        return context




#possibly get_context_data POST part is repetative with the post function, could be refactored
class FirsStepView(LoginRequiredMixin, UserRoleContextMixin, UserPassesTestMixin, TemplateView):
    """
    Handles the first step of the order creation process.
    Includes forms for location, decoration, utility, and common information.
    """

    model = Order
    model_object = Object
    template_name = "order_first_step.html"

    form_house = HouseForm
    form_land = LandForm
    form_apartament = ApartamentForm
    form_cottage = CottageForm
    form_location = ObjectLocationForm
    form_decoration = DecorationForm
    form_utility = UtilityForm
    form_common_info = CommonInformationForm

    def test_func(self):
        return not (self.request.user.groups.filter(name='Agency').exists() or self.request.user.groups.filter(name='Evaluator').exists())

    def handle_no_permission(self):
        messages.error(self.request, NO_PERMISSION_MESSAGE)
        return redirect('core.uauth:login')


    def get_queryset(self):
        user = self.request.user

        if user.groups.filter(name='Agency').exists():
            return self.model.objects.filter(agency=user)
        
        return self.model.objects.none()


    def get_form_classes(self):
        return {
            'location_form': self.form_location,
            'decoration_form': self.form_decoration,
            'utility_form': self.form_utility,
            'common_info_form': self.form_common_info,
        }


    def get_context_data(self, **kwargs):
        """
        Prepares the context data for rendering the template.
        Initializes the forms based on the selected object type.
        """

        context = super().get_context_data(**kwargs)
        form_classes = self.get_form_classes()
        selected_obj_type = self.request.session.get('selected_obj_type')

        if self.request.method == 'POST':
            context.update({
                'location_form': form_classes['location_form'](self.request.POST),
                'decoration_form': form_classes['decoration_form'](self.request.POST),
                'utility_form': form_classes['utility_form'](self.request.POST),
                'common_info_form': form_classes['common_info_form'](self.request.POST),
            })

            match selected_obj_type:
                case 'Namas':
                    context['additional_form'] = self.form_house(self.request.POST)

                case 'Sklypas':
                    context['additional_form'] = self.form_land(self.request.POST)

                case 'Butas':
                    context['additional_form'] = self.form_apartament(self.request.POST)

                case 'Kotedžas':
                    context['additional_form'] = self.form_cottage(self.request.POST)

                case 'Sodas':
                    context['additional_form'] = self.form_house(self.request.POST)

                case _:
                    context['additional_form'] = None

        else:
            context.update({
                'location_form': form_classes['location_form'](),
                'decoration_form': form_classes['decoration_form'](),
                'utility_form': form_classes['utility_form'](),
                'common_info_form': form_classes['common_info_form'](),
            })

            match selected_obj_type:
                case 'Namas':
                    context['additional_form'] = self.form_house()

                case 'Sklypas':
                    context['additional_form'] = self.form_land()

                case 'Butas':
                    context['additional_form'] = self.form_apartament()

                case 'Kotedžas':
                    context['additional_form'] = self.form_cottage()

                case 'Sodas':
                    context['additional_form'] = self.form_house()

                case _:
                    context['additional_form'] = None

        context['selected_obj_type'] = selected_obj_type
        return context


    def post(self, request, *args, **kwargs):
        """
        Handles the POST request to create a new order.
        Validates the forms and saves the data if valid.
        """
        
        form_classes = self.get_form_classes()
        location_form = form_classes['location_form'](request.POST)
        decoration_form = form_classes['decoration_form'](request.POST)
        utility_form = form_classes['utility_form'](request.POST)
        common_info_form = form_classes['common_info_form'](request.POST)
        selected_obj_type = self.request.session.get('selected_obj_type')

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

            case _:
                additional_form = None

        if location_form.is_valid() and decoration_form.is_valid() and utility_form.is_valid() and common_info_form.is_valid() and (additional_form is None or additional_form.is_valid()):
            
            try:
                obj = self.model_object.objects.create(object_type=selected_obj_type)
                request.session['main_object_id'] = obj.id
                print("Object created with ID:", obj.id)

            except Exception as e:
                print("Error creating object:", e)
                return self.form_invalid(location_form, decoration_form, utility_form, common_info_form, additional_form)

            self.save_form_data(obj, location_form.cleaned_data)
            self.save_form_data(obj, decoration_form.cleaned_data)
            self.save_form_data(obj, utility_form.cleaned_data)
            self.save_form_data(obj, common_info_form.cleaned_data)

            if additional_form:
                self.save_form_data(obj, additional_form.cleaned_data)

            try:
                default_agency = User.objects.filter(groups__name='Agency', is_active=True).first()
                
                if not default_agency:
                    raise Exception("No active agency found")
                
                order = self.model.objects.create(
                    client=request.user,
                    agency=default_agency,
                    object=obj,
                    status=STATUS_CHOICES[0][0],
                    priority=PRIORITY_CHOICES[0][0]
                )
                request.session['order_id'] = order.id
                print("Order created successfully with ID:", order.id)

            except Exception as e:
                print("Error creating order:", e)
                return self.form_invalid(location_form, decoration_form, utility_form, common_info_form, additional_form)


            if selected_obj_type in ['Namas', 'Kotedžas']:
                return redirect('modules.orders:additional_buildings', object_id=obj.id)

            return redirect('modules.orders:select_agency', order_id=order.id)

        print("Form is invalid")
        print(location_form.errors)
        print(decoration_form.errors)
        print(utility_form.errors)
        print(common_info_form.errors)

        if additional_form:
            print(additional_form.errors)

        return self.form_invalid(location_form, decoration_form, utility_form, common_info_form, additional_form)


    def save_form_data(self, obj, cleaned_data):
        for key, value in cleaned_data.items():
            ObjectMeta.objects.create(ev_object=obj, meta_key=key, meta_value=value)


    def form_invalid(self, location_form, decoration_form, utility_form, common_info_form, additional_form=None):
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
        order = Order.objects.filter(object=obj).first()
        context['order'] = order
        context['order_id'] = order.id
        context['object'] = obj
        context['object_id'] = object_id
        context['is_evaluator'] = self.request.user.groups.filter(name='Evaluator').exists()
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
            order = Order.objects.filter(object=obj).first()
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
            return self.model.objects.filter(agency=user)
        
        return self.model.objects.filter(client=user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('Užsakymų sąrašas')
        context['user_is_agency'] = self.request.user.groups.filter(name='Agency').exists()
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
        context['order_id'] = self.kwargs.get('order_id')
        agencies = self.get_queryset()
        agency_data = []

        ongoing_status = STATUS_CHOICES[2][0]  # 'Vykdomas'
        completed_status = STATUS_CHOICES[3][0]  # 'Įvykdytas'

        for agency in agencies:
            evaluators = agency.evaluators.all()
            ongoing_orders_count = sum(evaluator.evaluator_orders.filter(status=ongoing_status).count() for evaluator in evaluators)
            completed_orders_count = sum(evaluator.evaluator_orders.filter(status=completed_status).count() for evaluator in evaluators)

            agency_data.append({
                'id': agency.id,
                'name': self.model_user_meta.get_meta(agency, 'agency_name'),
                'date_joined': agency.date_joined,
                'evaluator_count': agency.evaluator_count,
                'ongoing_orders': ongoing_orders_count,
                'completed_orders': completed_orders_count,
                'evaluation_starting_price': self.model_user_meta.get_meta(agency, 'evaluation_starting_price'),
            })

        context['agency_data'] = agency_data
        context['title'] = 'Select an Agency'
        return context

    def post(self, request, *args, **kwargs):
        selected_agency_id = request.POST.get('selected_agency_id')

        if selected_agency_id:
            try:
                selected_agency = self.model.objects.get(id=selected_agency_id, groups__name='Agency')
                order_id = request.session.get('main_object_id')
                order = self.model_order.objects.get(object_id=order_id)
                order.agency = selected_agency

                # Select the appraiser with the least amount of orders
                appraisers = self.model.objects.filter(groups__name='Evaluator', agency=selected_agency)
                appraiser_with_least_orders = min(appraisers, key=lambda appraiser: appraiser.evaluator_orders.count())

                # Associate the order with the selected appraiser
                order.evaluator = appraiser_with_least_orders
                order.status = STATUS_CHOICES[1][0]  # 'Naujas'
                order.save()

                return redirect('modules.orders:order_list')
            except self.model.DoesNotExist:
                return redirect('modules.orders:select_agency')
            except self.model.DoesNotExist:
                return redirect('modules.orders:order_first_step')
            
        return redirect('modules.orders:select_agency')
    




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