import requests
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from shared.mixins.mixins import UserRoleContextMixin
from core.uauth.models import UserMeta
from modules.orders.models import Object, Order, NearbyOrganization
from django.utils.translation import gettext as _
from requests.exceptions import RequestException
from geopy.distance import geodesic
from decimal import Decimal
from django.contrib import messages
from modules.evaluator.forms import NearbyOrganizationForm

# Global context variables
TOTAL_STEPS = 8
SHOW_PROGRESS_BAR = True

class GenerateReportView(LoginRequiredMixin, UserRoleContextMixin, TemplateView):
    template_name = "generate_report.html"
    login_url = 'core.uauth:login'
    redirectfield_name = 'next'
    user_meta = UserMeta

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
        context['show_progress_bar'] = SHOW_PROGRESS_BAR
        context['current_step'] = 8
        context['total_steps'] = TOTAL_STEPS
        return context
