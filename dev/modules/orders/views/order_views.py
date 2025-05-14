from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.views.generic import ListView, View, DetailView
from django.urls import reverse_lazy
from django.utils.translation import gettext as _
from modules.orders.enums import MUNICIPALITY_CHOICES, STATUS_CHOICES, PRIORITY_CHOICES, ObjectImages
from modules.orders.models import Order, Object, ObjectMeta
from core.uauth.models import User, UserMeta
from django.db.models import Count, Q, F
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from shared.mixins.mixins import UserRoleContextMixin
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.utils import timezone


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

            for key in ['location_data', 'additional_data', 'decoration_data', 'common_info_data', 'utility_data']:

                if key in request.session:
                    del request.session[key]

            return redirect('modules.orders:order_creation_step')
        
        messages.error(request, _('Please select an object type'))

        return redirect('modules.orders:selection')


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _('Užsisakykite NT vertinimą')
        return context


    

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
        context['is_evaluator'] = self.request.user.groups.filter(name='Evaluator').exists()

        context['municipality_choices'] = MUNICIPALITY_CHOICES
        context['status_choices'] = STATUS_CHOICES
        context['priority_choices'] = PRIORITY_CHOICES

        evaluator_phones = {}
        for order in context['orders']:
            if order.evaluator and order.evaluator.id not in evaluator_phones:
                phone = UserMeta.get_meta(order.evaluator, 'phone_num')
                evaluator_phones[order.evaluator.id] = phone

            now = timezone.now()
            future_events = order.events.filter(start_time__gt=now).order_by('start_time')
            order.first_future_event = future_events.first() if future_events.exists() else None

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
        context['now'] = timezone.now()
        context['municipality_choices'] = MUNICIPALITY_CHOICES
        context['status_choices'] = STATUS_CHOICES
        context['priority_choices'] = PRIORITY_CHOICES
        context['is_agency'] = self.request.user.groups.filter(name='Agency').exists()
        context['is_evaluator'] = self.request.user.groups.filter(name='Evaluator').exists()
        now = timezone.now()
        
        for order in context['orders']:
            future_events = order.events.filter(start_time__gt=now).order_by('start_time')
            order.first_future_event = future_events.first() if future_events.exists() else None

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

        ObjectMeta.objects.filter(ev_object=obj).delete()
        obj.delete()
        order.delete()

        messages.success(request, "Užsakymas ištrintas sėkmingai.")
        return HttpResponseRedirect(reverse_lazy('modules.orders:order_list'))




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
        
        order_id = self.kwargs.get('order_id')
        object_id = self.kwargs.get('object_id')
        
        if order_id:
            context['order_id'] = order_id
        elif object_id:
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
                'evaluator_count': evaluators.count(),
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
                
                order_id = self.kwargs.get('order_id')
                object_id = self.kwargs.get('object_id')
                
                if order_id:
                    order = get_object_or_404(Order, id=order_id)
                    order.agency = selected_agency
                    order.save()
                    
                elif object_id:
                    obj = get_object_or_404(Object, id=object_id)
                    order = Order.objects.create(
                        client=request.user,
                        object=obj,
                        agency=selected_agency,
                        status='Naujas' 
                    )
                    
                    appraisers = self.model.objects.filter(groups__name='Evaluator', agency=selected_agency)
                    if appraisers.exists():
                        appraiser_with_least_orders = min(appraisers, key=lambda appraiser: appraiser.evaluator_orders.count())
                        order.evaluator = appraiser_with_least_orders
                        order.save()
                
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




class ReportAccessView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    View to check permissions before serving a report file.
    """
    def test_func(self):
        order_id = self.kwargs.get('order_id')
        order = get_object_or_404(Order, id=order_id)
        user = self.request.user
        
        # Check if user has permission to access this report
        if user.groups.filter(name__in=['Agency', 'Evaluator']).exists():
            return True
            
        # The evaluator assigned to this order can access
        if order.evaluator == user:
            return True
            
        # If client is the owner of the order, they can access only if report is approved
        if order.client == user:
            return hasattr(order, 'report') and order.report and order.report.status == 'approved'
            
        return False
    
    def handle_no_permission(self):
        messages.error(self.request, _("Ataskaita dar nėra patvirtinta arba neturite teisės ją peržiūrėti."))
        return redirect('modules.orders:order_list')
    
    def get(self, request, *args, **kwargs):
        order_id = self.kwargs.get('order_id')
        order = get_object_or_404(Order, id=order_id)
        
        if not hasattr(order, 'report') or not order.report or not order.report.report_file:
            messages.error(request, _("Ataskaita neegzistuoja."))
            return redirect('modules.orders:order_list')
            
        # Serve the report file
        return redirect(order.report.report_file.url)