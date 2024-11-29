from django.conf import settings
from django.shortcuts import render, redirect
from modules.orders.enums import ObjectImages
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView, CreateView, ListView, FormView, View, UpdateView
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from django.forms import formset_factory
from modules.orders.enums import *
from modules.orders.models import *
from modules.orders.forms import *
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.decorators import login_required
from core.uauth.models import User, UserMeta
from django.db.models import Count, Q
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin

def index(request):
    return render(request, 'orders/index.html')

def test_view(request):
    return render(request, 'shared/header.html')


class LandingView(LoginRequiredMixin, ListView):
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
        context['is_agency'] = self.request.user.groups.filter(name='Agency').exists()
        context['is_evaluator'] = self.request.user.groups.filter(name='Evaluator').exists()
        return context


#possibly get_context_data POST part is repetative with the post function, could be refactored
class FirsStepView(LoginRequiredMixin, TemplateView):
    template_name = "order_first_step.html"

    def get_queryset(self):
        user = self.request.user

        if user.groups.filter(name='Agency').exists():
            return Order.objects.filter(agency=user)
        
        return Order.objects.none()

    def get_form_classes(self):
        return {
            'location_form': ObjectLocationForm,
            'decoration_form': DecorationForm,
            'utility_form': UtilityForm,
            'common_info_form': CommonInformationForm,
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_agency'] = self.request.user.groups.filter(name='Agency').exists()
        form_classes = self.get_form_classes()
        selected_obj_type = self.request.session.get('selected_obj_type')

        if self.request.method == 'POST':
            context.update({
                'location_form': form_classes['location_form'](self.request.POST),
                'decoration_form': form_classes['decoration_form'](self.request.POST),
                'utility_form': form_classes['utility_form'](self.request.POST),
                'common_info_form': form_classes['common_info_form'](self.request.POST),
            })

            if selected_obj_type == 'Namas':
                context['additional_form'] = HouseForm(self.request.POST)

            elif selected_obj_type == 'Sklypas':
                context['additional_form'] = LandForm(self.request.POST)

            elif selected_obj_type == 'Butas':
                context['additional_form'] = ApartamentForm(self.request.POST)

            elif selected_obj_type == 'Kotedžas':
                context['additional_form'] = CottageForm(self.request.POST)

            elif selected_obj_type == 'Sodas':
                context['additional_form'] = HouseForm(self.request.POST)

        else:
            context.update({
                'location_form': form_classes['location_form'](),
                'decoration_form': form_classes['decoration_form'](),
                'utility_form': form_classes['utility_form'](),
                'common_info_form': form_classes['common_info_form'](),
            })

            if selected_obj_type == 'Namas':
                context['additional_form'] = HouseForm()

            elif selected_obj_type == 'Sklypas':
                context['additional_form'] = LandForm()

            elif selected_obj_type == 'Butas':
                context['additional_form'] = ApartamentForm()

            elif selected_obj_type == 'Kotedžas':
                context['additional_form'] = CottageForm()

            elif selected_obj_type == 'Sodas':
                context['additional_form'] = HouseForm()

        context['selected_obj_type'] = selected_obj_type
        return context

    def post(self, request, *args, **kwargs):
        form_classes = self.get_form_classes()
        location_form = form_classes['location_form'](request.POST)
        decoration_form = form_classes['decoration_form'](request.POST)
        utility_form = form_classes['utility_form'](request.POST)
        common_info_form = form_classes['common_info_form'](request.POST)
        selected_obj_type = self.request.session.get('selected_obj_type')

        if selected_obj_type == 'Namas':
            additional_form = HouseForm(request.POST)

        elif selected_obj_type == 'Sklypas':
            additional_form = LandForm(request.POST)

        elif selected_obj_type == 'Butas':
            additional_form = ApartamentForm(request.POST)

        elif selected_obj_type == 'Kotedžas':
            additional_form = CottageForm(request.POST)

        elif selected_obj_type == 'Sodas':
            additional_form = HouseForm(request.POST)

        else:
            additional_form = None

        if location_form.is_valid() and decoration_form.is_valid() and utility_form.is_valid() and common_info_form.is_valid() and (additional_form is None or additional_form.is_valid()):
            
            try:
                obj = Object.objects.create(object_type=selected_obj_type)
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
                
                Order.objects.create(
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
    template_name = 'additional_buildings.html'
    #success_url = 'modules.orders:additional_buildings'
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
            obj = Object.objects.get(id=obj_id)

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
            Object.save_meta(obj, key, value)

    def form_invalid(self, garage_formset, shed_formset, gazebo_formset):
        context = self.get_context_data()
        context.update({
            'garage_formset': garage_formset,
            'shed_formset': shed_formset,
            'gazebo_formset': gazebo_formset,
        })

        return self.render_to_response(context)
    

class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = "order_list.html"
    context_object_name = "orders"
    login_url = 'core.uauth:login'
    redirect_field_name = 'next'

    def get_queryset(self):
        user = self.request.user

        if user.groups.filter(name='Agency').exists():
            return Order.objects.filter(agency=user)
            
        return Order.objects.filter(client=user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_agency'] = self.request.user.groups.filter(name='Agency').exists()
        context['is_evaluator'] = self.request.user.groups.filter(name='Evaluator').exists()
        return context


class OrderDeleteView(View):
    def post(self, request, *args, **kwargs):
        order_id = kwargs.get('pk')
        order = Order.objects.get(id=order_id)
        obj = order.object

        ObjectMeta.objects.filter(ev_object=obj).delete()
        obj.delete()
        order.delete()

        return HttpResponseRedirect(reverse_lazy('modules.orders:order_list'))

class ObjectUpdateView(UpdateView):
    model = Object
    template_name = "user_edit_order.html"
    success_url = reverse_lazy('modules.orders:order_list')
    fields = []

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
        context['decoration_form'] = DecorationForm(initial=initial_data)
        context['utility_form'] = UtilityForm(initial=initial_data)
        context['common_info_form'] = CommonInformationForm(initial=initial_data)

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

        return context

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        self.object = obj
        initial_data = self.get_initial_data(obj)
        location_form = ObjectLocationForm(request.POST, initial=initial_data)
        decoration_form = DecorationForm(request.POST, initial=initial_data)
        utility_form = UtilityForm(request.POST, initial=initial_data)
        common_info_form = CommonInformationForm(request.POST, initial=initial_data)

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
            Object.save_meta(obj, key, value)


class EditAdditionalBuildingsView(UpdateView):
    model = Object
    template_name = "edit_additional_buildings.html"
    success_url = reverse_lazy('modules.orders:order_list')
    fields = []

    def get_forms(self):
        garage_data = ObjectMeta.objects.filter(ev_object=self.object, meta_key__startswith='garage_')
        shed_data = ObjectMeta.objects.filter(ev_object=self.object, meta_key__startswith='shed_')
        gazebo_data = ObjectMeta.objects.filter(ev_object=self.object, meta_key__startswith='gazebo_')
        
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
        forms = self.get_forms()
        context.update(forms)
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        forms = self.get_forms()
        garage_form = forms.get('garage_form')
        shed_form = forms.get('shed_form')
        gazebo_form = forms.get('gazebo_form')

        if garage_form:
            garage_form = GarageForm(request.POST, prefix='garage')

        if shed_form:
            shed_form = ShedForm(request.POST, prefix='shed')

        if gazebo_form:
            gazebo_form = GazeboForm(request.POST, prefix='gazebo')

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
            Object.save_meta(obj, key, value)


class AgencySelectionView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'agency_selection.html'
    context_object_name = 'agencies'
    login_url = 'core.uauth:login'
    redirect_field_name = 'next'

    def get_queryset(self):
        return User.objects.filter(groups__name='Agency').annotate(
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
                'name': UserMeta.get_meta(agency, 'agency_name'),
                'date_joined': agency.date_joined,
                'evaluator_count': agency.evaluator_count,
                'completed_orders': agency.completed_orders,
                'evaluation_starting_price': UserMeta.get_meta(agency, 'evaluation_starting_price'),
            })

        context['agency_data'] = agency_data
        context['title'] = 'Select an Agency'
        return context

    def post(self, request, *args, **kwargs):
        selected_agency_id = request.POST.get('selected_agency_id')

        if selected_agency_id:
            try:
                selected_agency = User.objects.get(id=selected_agency_id, groups__name='Agency')
                order_id = request.session.get('main_object_id')
                order = Order.objects.get(object_id=order_id)
                order.agency = selected_agency
                order.save()
                return redirect('modules.orders:order_list')
            except User.DoesNotExist:
                return redirect('modules.orders:select_agency')
            except Order.DoesNotExist:
                return redirect('modules.orders:order_first_step')
            
        return redirect('modules.orders:select_agency')