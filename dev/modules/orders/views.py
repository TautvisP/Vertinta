from django.shortcuts import render, redirect
from modules.orders.enums import ObjectImages
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView, ListView, View, UpdateView
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.forms import formset_factory
from modules.orders.enums import MUNICIPALITY_CHOICES
from modules.orders.models import Order, Object, ObjectMeta
from modules.orders.forms import HouseForm, LandForm, ApartamentForm, CottageForm, ObjectLocationForm, DecorationForm, UtilityForm, CommonInformationForm, GarageForm, ShedForm, GazeboForm
from core.uauth.models import User, UserMeta
from django.db.models import Count, Q
from django.contrib.auth.mixins import LoginRequiredMixin
from shared.mixins.mixins import UserRoleContextMixin

def index(request):
    return render(request, 'orders/index.html')

def test_view(request):
    return render(request, 'shared/header.html')


class LandingView(LoginRequiredMixin, UserRoleContextMixin, ListView):
    """
    Displays a list of object images for the landing page.
    Requires the user to be logged in and have the appropriate role.
    """

    template_name = "object_select.html"
    login_url = 'core.uauth:login'
    redirect_field_name = 'next'

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
class FirsStepView(LoginRequiredMixin, UserRoleContextMixin, TemplateView):
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
                
                self.model.objects.create(
                    client=request.user,
                    agency=default_agency,
                    object=obj,
                    status='Naujas'
                )
                print("Order created successfully")

            except Exception as e:
                print("Error creating order:", e)
                return self.form_invalid(location_form, decoration_form, utility_form, common_info_form, additional_form)

            if selected_obj_type in ['Namas', 'Kotedžas']:
                return redirect('modules.orders:additional_buildings')

            return redirect('modules.orders:select_agency')

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




class AdditionalBuildingsView(TemplateView):
    """
    Handles the additional buildings step in the order creation process.
    Includes formsets for garage, shed, and gazebo data.
    """
        
    model = Object
    template_name = 'additional_buildings.html'
    success_url = 'modules.orders:select_agency'

    def get_formsets(self):
        GarageFormSet = formset_factory(GarageForm, extra=1)
        ShedFormSet = formset_factory(ShedForm, extra=1)
        GazeboFormSet = formset_factory(GazeboForm, extra=1)

        return {
            'garage_formset': GarageFormSet,
            'shed_formset': ShedFormSet,
            'gazebo_formset': GazeboFormSet,
        }


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        formsets = self.get_formsets()

        if self.request.method == 'POST':
            context.update({
                'garage_formset': formsets['garage_formset'](self.request.POST, prefix='garages'),
                'shed_formset': formsets['shed_formset'](self.request.POST, prefix='sheds'),
                'gazebo_formset': formsets['gazebo_formset'](self.request.POST, prefix='gazebos'),
            })

        else:
            context.update({
                'garage_formset': formsets['garage_formset'](prefix='garages'),
                'shed_formset': formsets['shed_formset'](prefix='sheds'),
                'gazebo_formset': formsets['gazebo_formset'](prefix='gazebos'),
            })

        return context


    def post(self, request, *args, **kwargs):
        formsets = self.get_formsets()
        garage_formset = formsets['garage_formset'](request.POST, prefix='garages')
        shed_formset = formsets['shed_formset'](request.POST, prefix='sheds')
        gazebo_formset = formsets['gazebo_formset'](request.POST, prefix='gazebos')

        if garage_formset.is_valid() or shed_formset.is_valid() or gazebo_formset.is_valid():
            obj_id = request.session.get('main_object_id')
            obj = self.model.objects.get(id=obj_id)

            for garage_form in garage_formset:
                self.save_form_data(obj, garage_form.cleaned_data)

            for shed_form in shed_formset:
                self.save_form_data(obj, shed_form.cleaned_data)

            for gazebo_form in gazebo_formset:
                self.save_form_data(obj, gazebo_form.cleaned_data)

            return redirect(self.success_url)
        
        return self.form_invalid(garage_formset, shed_formset, gazebo_formset)
    

    def save_form_data(self, obj, cleaned_data):

        for key, value in cleaned_data.items():
            self.model.save_meta(obj, key, value)


    def form_invalid(self, garage_formset, shed_formset, gazebo_formset):
        context = self.get_context_data()
        context.update({
            'garage_formset': garage_formset,
            'shed_formset': shed_formset,
            'gazebo_formset': gazebo_formset,
        })

        return self.render_to_response(context)
    

    

class OrderListView(LoginRequiredMixin, UserRoleContextMixin, ListView):
    """
    Displays a list of orders for the current user.
    Requires the user to be logged in and have the appropriate role.
    """
        
    model = Order
    template_name = "order_list.html"
    context_object_name = "orders"
    login_url = 'core.uauth:login'
    redirect_field_name = 'next'

    def get_queryset(self):
        user = self.request.user

        if user.groups.filter(name='Agency').exists():
            return self.model.objects.filter(agency=user)
        
        return self.model.objects.filter(client=user)


class EvaluatorOrderListView(LoginRequiredMixin, UserRoleContextMixin, ListView):
    """
    Displays a list of orders for the evaluator.
    Requires the user to be logged in and have the appropriate role.
    """

    model = Order
    template_name = "evaluator_order_list.html"
    context_object_name = "orders"
    login_url = 'core.uauth:login'
    redirect_field_name = 'next'

    def get_queryset(self):
        user = self.request.user
        queryset = self.model.objects.filter(evaluator=user)

        municipality = self.request.GET.get('municipality')
        if municipality:
            queryset = queryset.filter(object__objectmeta__meta_key='municipality', object__objectmeta__meta_value=municipality)

        return queryset


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['municipality_choices'] = MUNICIPALITY_CHOICES
        return context
    



class OrderDeleteView(View):
    """
    Handles the deletion of an order.
    Deletes the associated object and its metadata.
    """
    
    def post(self, request, *args, **kwargs):
        order_id = kwargs.get('pk')
        order = Order.objects.get(id=order_id)
        obj = order.object

        ObjectMeta.objects.filter(ev_object=obj).delete()
        obj.delete()
        order.delete()

        return HttpResponseRedirect(reverse_lazy('modules.orders:order_list'))



class ObjectUpdateView(UpdateView):
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




class EditAdditionalBuildingsView(UpdateView):
    """
    Handles the editing of additional buildings associated with an object.
    Includes forms for garage, shed, and gazebo data.
    """
        
    model = Object
    model_object = ObjectMeta
    template_name = "edit_additional_buildings.html"
    success_url = reverse_lazy('modules.orders:order_list')
    fields = []

    form_garage = GarageForm
    form_shed = ShedForm
    form_gazebo = GazeboForm


    def get_forms(self):
        garage_data = self.model_object.objects.filter(ev_object=self.object, meta_key__startswith='garage_')
        shed_data = self.model_object.objects.filter(ev_object=self.object, meta_key__startswith='shed_')
        gazebo_data = self.model_object.objects.filter(ev_object=self.object, meta_key__startswith='gazebo_')
        
        forms = {}

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


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        forms = self.get_forms()
        context.update(forms)
        context['show_progress_bar'] = False
        context['is_evaluator'] = False 
        return context


    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        forms = self.get_forms()
        garage_form = forms.get('garage_form')
        shed_form = forms.get('shed_form')
        gazebo_form = forms.get('gazebo_form')

        if garage_form:
            garage_form = self.form_garage(request.POST, prefix='garage')

        if shed_form:
            shed_form = self.form_shed(request.POST, prefix='shed')

        if gazebo_form:
            gazebo_form = self.form_gazebo(request.POST, prefix='gazebo')

        if (not garage_form or garage_form.is_valid()) and (not shed_form or shed_form.is_valid()) and (not gazebo_form or gazebo_form.is_valid()):
            self.save_additional_buildings(self.object, garage_form, shed_form, gazebo_form)
            return redirect(self.success_url)
        
        return self.form_invalid(garage_form, shed_form, gazebo_form)


    def form_invalid(self, garage_form, shed_form, gazebo_form):
        context = self.get_context_data()

        if garage_form:
            context['garage_form'] = garage_form

        if shed_form:
            context['shed_form'] = shed_form

        if gazebo_form:
            context['gazebo_form'] = gazebo_form

        return self.render_to_response(context)


    def save_additional_buildings(self, obj, garage_form, shed_form, gazebo_form):

        if garage_form:
            self.save_form_data(obj, garage_form.cleaned_data)

        if shed_form:
            self.save_form_data(obj, shed_form.cleaned_data)

        if gazebo_form:
            self.save_form_data(obj, gazebo_form.cleaned_data)

    def save_form_data(self, obj, cleaned_data):
        for key, value in cleaned_data.items():
            self.model.save_meta(obj, key, value)




class AgencySelectionView(LoginRequiredMixin, ListView):
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

    def get_queryset(self):
        return self.model.objects.filter(groups__name='Agency').annotate(
            evaluator_count=Count('evaluators'),
            completed_orders=Count('orders', filter=Q(orders__status='completed'))
        )


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        agencies = self.get_queryset()
        agency_data = []

        for agency in agencies:
            agency_data.append({
                'id': agency.id,
                'name': self.model_user_meta.get_meta(agency, 'agency_name'),
                'date_joined': agency.date_joined,
                'evaluator_count': agency.evaluator_count,
                'completed_orders': agency.completed_orders,
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
                # Possibly this function isnt working, because the same evaluator is assigned to all orders
                appraisers = self.model.objects.filter(groups__name='Evaluator', agency=selected_agency)
                appraiser_with_least_orders = min(appraisers, key=lambda appraiser: appraiser.orders.count())


                #appraiser_with_least_orders = User.objects.get(id=13)
                # Associate the order with the selected appraiser
                order.evaluator = appraiser_with_least_orders
                order.save()

                return redirect('modules.orders:order_list')
            except self.model.DoesNotExist:
                return redirect('modules.orders:select_agency')
            except self.model.DoesNotExist:
                return redirect('modules.orders:order_first_step')
            
        return redirect('modules.orders:select_agency')