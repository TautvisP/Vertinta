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


class FoundNearbyOrganizationView(LoginRequiredMixin, UserRoleContextMixin, TemplateView):
    model = Object
    user_meta = UserMeta
    template_name = "found_nearby_objects.html"
    login_url = 'core.uauth:login'
    redirect_field_name = 'next'

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
        context['current_step'] = 7
        context['total_steps'] = TOTAL_STEPS

        # Filters
        object_type = self.request.GET.get('object_type', 'all')
        search_radius = int(self.request.GET.get('search_radius', 2000))

        if obj.latitude is None or obj.longitude is None:
            context['nearby_organizations'] = []
            return context

        nearby_organizations = self.find_nearby_organizations(obj.latitude, obj.longitude, object_type, search_radius)
        context['nearby_organizations'] = nearby_organizations
        context['object_type'] = object_type
        context['search_radius'] = search_radius

        return context

    def post(self, request, *args, **kwargs):
        order_id = self.kwargs.get('order_id')
        order = get_object_or_404(Order, id=order_id)
        obj = order.object

        name = request.POST.get('name')
        latitude = Decimal(request.POST.get('latitude')).quantize(Decimal('1.000000'))
        longitude = Decimal(request.POST.get('longitude')).quantize(Decimal('1.000000'))
        address = request.POST.get('address')
        distance = Decimal(request.POST.get('distance'))
        category = request.POST.get('category')

        # Check if the organization already exists
        existing_organization = NearbyOrganization.objects.filter(
            object=obj,
            name__iexact=name.strip(),
            latitude=latitude,        
            longitude=longitude,
        ).first()

        if existing_organization:
            messages.warning(request, 'Organization already exists in the database.')
            return redirect('modules.evaluator:found_organizations', order_id=order_id, pk=obj.pk)

        # If no match, create a new entry
        NearbyOrganization.objects.create(
            object=obj,
            name=name.strip(),
            latitude=latitude,
            longitude=longitude,
            address=address.strip(),
            distance=distance,
            category=category.strip()
        )

        return redirect('modules.evaluator:found_organizations', order_id=order_id, pk=obj.pk)

    def find_nearby_organizations(self, latitude, longitude, object_type, search_radius):
        overpass_url = "http://overpass-api.de/api/interpreter"
        types = {
            'school': 'node["amenity"="school"]',
            'hospital': 'node["amenity"="hospital"]',
            'supermarket': 'node["shop"="supermarket"]',
            'pharmacy': 'node["amenity"="pharmacy"]',
            'bakery': 'node["shop"="bakery"]',
            'police': 'node["amenity"="police"]',
            'fire_station': 'node["amenity"="fire_station"]',
            'post_office': 'node["amenity"="post_office"]'
        }

        if object_type == 'all':
            overpass_query = f"""
            [out:json];
            (
              {types['school']}(around:{search_radius},{latitude},{longitude});
              {types['hospital']}(around:{search_radius},{latitude},{longitude});
              {types['supermarket']}(around:{search_radius},{latitude},{longitude});
              {types['pharmacy']}(around:{search_radius},{latitude},{longitude});
              {types['bakery']}(around:{search_radius},{latitude},{longitude});
              {types['police']}(around:{search_radius},{latitude},{longitude});
              {types['fire_station']}(around:{search_radius},{latitude},{longitude});
              {types['post_office']}(around:{search_radius},{latitude},{longitude});
            );
            out body;
            """

        else:
            overpass_query = f"""
            [out:json];
            (
              {types[object_type]}(around:{search_radius},{latitude},{longitude});
            );
            out body;
            """

        try:
            response = requests.get(overpass_url, params={'data': overpass_query})
            response.raise_for_status()
            results = response.json()
            nearby_organizations = []

            for element in results['elements']:
                name = element.get('tags', {}).get('name', 'Unknown')
                lat = Decimal(str(element['lat'])).quantize(Decimal('1.000000'))
                lon = Decimal(str(element['lon'])).quantize(Decimal('1.000000'))
                address = element.get('tags', {}).get('addr:street', '') + ', ' + element.get('tags', {}).get('addr:city', '')

                # Some organizations only have a comma as their address
                if address.strip() == ',':
                    continue

                distance = self.calculate_distance(latitude, longitude, lat, lon) * 1000  # Converting to meters
                distance = round(distance)
                category = element.get('tags', {}).get('amenity') or element.get('tags', {}).get('shop') or 'other'

                nearby_organizations.append({
                    'name': name,
                    'latitude': lat,
                    'longitude': lon,
                    'address': address,
                    'distance': distance,
                    'category': category
                })

            return nearby_organizations
        
        except RequestException as e:
            print(f"Error fetching data from Overpass API: {e}")
            return []
        
        except ValueError as e:
            print(f"Error decoding JSON response: {e}")
            return []

    def calculate_distance(self, lat1, lon1, lat2, lon2):
        return geodesic((lat1, lon1), (lat2, lon2)).kilometers




class NearbyOrganizationListView(LoginRequiredMixin, UserRoleContextMixin, TemplateView):
    template_name = "nearby_object_list.html"
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
        context['current_step'] = 7
        context['total_steps'] = TOTAL_STEPS
        context['added_nearby_organizations'] = obj.nearby_organizations.all()
        return context




class DeleteNearbyOrganizationView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        organization_id = self.kwargs.get('organization_id')
        organization = get_object_or_404(NearbyOrganization, id=organization_id)
        order_id = organization.object.order_set.first().id
        organization.delete()
        return redirect('modules.evaluator:nearby_organization_list', order_id=order_id, pk=organization.object.id)




class AddNearbyOrganizationView(LoginRequiredMixin, UserRoleContextMixin, TemplateView):
    template_name = "add_nearby_organization.html"
    login_url = 'core.uauth:login'
    redirect_field_name = 'next'
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
        context['current_step'] = 7
        context['total_steps'] = TOTAL_STEPS
        context['form'] = NearbyOrganizationForm()
        return context


    def post(self, request, *args, **kwargs):
        order_id = self.kwargs.get('order_id')
        order = get_object_or_404(Order, id=order_id)
        obj = order.object

        form = NearbyOrganizationForm(request.POST)

        if form.is_valid():
            name = form.cleaned_data['name']
            category = form.cleaned_data['category']
            address = form.cleaned_data['address']
            distance = form.cleaned_data['distance']
            latitude = form.cleaned_data['latitude']
            longitude = form.cleaned_data['longitude']

            # Check if the organization already exists
            existing_organization = NearbyOrganization.objects.filter(
                object=obj,
                name__iexact=name.strip(),
                latitude=latitude,
                longitude=longitude,
            ).first()

            if existing_organization:
                messages.warning(request, 'Organization already exists in the database.')
                return redirect('modules.evaluator:add_nearby_organization', order_id=order_id, pk=obj.pk)
            

            # If no match, create a new entry
            NearbyOrganization.objects.create(
                object=obj,
                name=name.strip(),
                latitude=latitude,
                longitude=longitude,
                address=address.strip(),
                distance=distance,
                category=category.strip()
            )

            messages.success(request, 'Organization added successfully.')
            return redirect('modules.evaluator:nearby_organization_list', order_id=order_id, pk=obj.pk)

        context = self.get_context_data(**kwargs)
        context['form'] = form
        return self.render_to_response(context)