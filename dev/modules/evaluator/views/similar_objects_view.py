"""
This view contains logic for similar object search and manipulation to the one being evaluated. 
Contains web scraping logic to automatically find similar objects on aruodas.lt (not implemented as of yet).
Contains logic for manually adding and editing similar objects.
Contains logic for displaying found and added similar objects.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from core.uauth.models import UserMeta
from shared.mixins.mixins import UserRoleContextMixin
from modules.orders.models import Object, Order, SimilarObject, SimilarObjectMetadata
from django.views.generic import TemplateView
from modules.orders.forms import ObjectLocationForm, HouseForm, LandForm, ApartamentForm, CottageForm, DecorationForm, CommonInformationForm, UtilityForm
from modules.evaluator.forms import SimilarObjectTypeSelectionForm, ButasSearchForm, NamasSearchForm, PatalposSearchForm, SklypaiSearchForm, SimilarObjectForm
from django.views import View
from django.utils.translation import gettext as _
from django.template.loader import render_to_string
import requests
from bs4 import BeautifulSoup
from django.http import JsonResponse, HttpResponseBadRequest
from shared.mixins.evaluator_access_mixin import EvaluatorAccessMixin
from django.contrib import messages



# Global context variables
TOTAL_STEPS = 8
SHOW_PROGRESS_BAR = True

class SimilarObjectSearchView(LoginRequiredMixin, EvaluatorAccessMixin, UserRoleContextMixin, TemplateView):
    """
    This function still needs to be developed. Currently aruodas scraper is not working because of the human verification
    """

    model_meta = UserMeta
    template_name = 'similar_object_search.html'
    result_template_name = 'similar_object_results.html'
    login_url = 'core.uauth:login'
    redirect_field_name = 'next'

    form_class_object_type = SimilarObjectTypeSelectionForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_id = self.kwargs.get('order_id')
        pk = self.kwargs.get('pk')
        order = get_object_or_404(Order, id=order_id)
        obj = get_object_or_404(Object, id=pk)
        client = order.client
        phone_number = self.model_meta.get_meta(client, 'phone_num')
        context['order'] = order
        context['object'] = obj
        context['client'] = client
        context['phone_number'] = phone_number
        context['order_id'] = order_id
        context['pk'] = pk
        context['show_progress_bar'] = SHOW_PROGRESS_BAR
        context['is_evaluator'] = True
        context['current_step'] = 5
        context['total_steps'] = TOTAL_STEPS
        context['form'] = self.form_class_object_type()
        return context


    def post(self, request, *args, **kwargs):
        order_id = self.kwargs.get('order_id')
        pk = self.kwargs.get('pk')
        object_type = request.POST.get('object_type')
        form_class = self.get_form_class(object_type)

        if form_class is None:
            print(f"Invalid object type: {object_type}")
            return HttpResponseBadRequest(f"Invalid object type: {object_type}")
        
        form = form_class(request.POST)
        context = self.get_context_data(order_id=order_id, pk=pk)
        
        if form.is_valid():
            data = form.cleaned_data
            listings = self.scrape_aruodas(data, object_type)
            context['form'] = form
            context['listings'] = listings
            return render(request, self.result_template_name, context)
        
        context['form'] = form
        return render(request, self.template_name, context)


    def get(self, request, *args, **kwargs):
        
        if 'object_type' in request.GET:
            object_type = request.GET.get('object_type')
            form_class = self.get_form_class(object_type)

            if form_class is None:
                print(f"Invalid object type: {object_type}")
                return HttpResponseBadRequest(f"Invalid object type: {object_type}")
            
            form = form_class()
            html = render_to_string('dynamic_form.html', {'form': form, 'object_type': object_type})
            return JsonResponse({'form': html})
        
        return super().get(request, *args, **kwargs)


    def get_form_class(self, object_type):
        form_classes = {
            'butai': ButasSearchForm,
            'namai': NamasSearchForm,
            'patalpos': PatalposSearchForm,
            'sklypai': SklypaiSearchForm,
        }
        form_class = form_classes.get(object_type)

        if form_class is None:
            print(f"No form class found for object_type: {object_type}")

        return form_class


    def scrape_aruodas(self, data, object_type):
        """
        Webscraper gets this result: It may happen when you are opening a large number of pages in a short period of time, or when there are other
        indications that resembles automated bot behaviour. In such cases we will ask to verify that a real person is
        using the website.
        """

        base_url = f'https://www.aruodas.lt/{object_type}/'
        params = self.get_aruodas_url_params(data, object_type)

        # Prepare the full URL with parameters
        request = requests.Request('GET', base_url, params=params).prepare()
        full_url = request.url
        print(f"Full URL: {full_url}")

        response = requests.get(full_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        listings = []

        for listing in soup.select('.advert'):
            title = listing.select_one('.list-item-title').get_text(strip=True)
            price = listing.select_one('.list-item-price').get_text(strip=True)
            link = listing.select_one('.list-item-title a')['href']
            print(f"Found listing Title: {title}, Price: {price}, Link: {link}")
            listings.append({'title': title, 'price': price, 'link': link})

        return listings


    def get_aruodas_url_params(self, data, object_type):
        params = {
            'detailed_search': '1',
            'FAreaOverAllMin': data.get('area_from'),
            'FAreaOverAllMax': data.get('area_to'),
            'FRoomNumMin': data.get('room_count_from'),
            'FRoomNumMax': data.get('room_count_to'),
            'FPriceMin': data.get('price_from'),
            'FPriceMax': data.get('price_to'),
            'FHouseState': ','.join(data.get('equipment', [])),
            'FWarmSystem': ','.join(data.get('heating', [])),
            'FHouseType': ','.join(data.get('building_type', [])),
        }
        return params
    



class EditSimilarObjectDataView(LoginRequiredMixin, EvaluatorAccessMixin, UserRoleContextMixin, TemplateView):    
    """
    This view handles both the creation of new similar objects and the editing of existing similar objects.
    It includes forms for similar object data, location data, and additional data based on the object type.
    """

    model = Object
    model_order = Order
    model_user_meta = UserMeta
    model_similar_object = SimilarObject
    template_name = 'edit_object.html'
    success_url_name = 'modules.evaluator:edit_similar_object_decoration'
    login_url = 'core.uauth:login'
    redirect_field_name = 'next'

    form_class_location = ObjectLocationForm
    form_class_house = HouseForm
    form_class_land = LandForm
    form_class_apartament = ApartamentForm
    form_class_cottage = CottageForm
    form_class_similar_object = SimilarObjectForm


    def get_object(self):
        order_id = self.kwargs.get('order_id')
        pk = self.kwargs.get('pk')
        return get_object_or_404(self.model, id=pk, order__id=order_id)


    def get_additional_form(self, object_type, data=None):

        match object_type:
            case 'Namas':
                return self.form_class_house(data)
            
            case 'Sklypas':
                return self.form_class_land(data)
            
            case 'Butas':
                return self.form_class_apartament(data)
            
            case 'Kotedžas':
                return self.form_class_cottage(data)
            
            case 'Sodas':
                return self.form_class_house(data)
            
            case _:
                return None


    def get_context_data(self, **kwargs):
        """
        Prepares the context data for rendering the template.
        Retrieves the order, object, and client information, and initializes the forms.
        If the user is editing an existing similar object, the form fields are populated with the existing data.
        """
        context = super().get_context_data(**kwargs)
        order_id = self.kwargs.get('order_id')
        pk = self.kwargs.get('pk')
        order = get_object_or_404(self.model_order, id=order_id)
        obj = get_object_or_404(self.model, id=pk)
        client = order.client
        phone_number = self.model_user_meta.get_meta(client, 'phone_num')
        context['order'] = order
        context['object'] = obj
        context['client'] = client
        context['phone_number'] = phone_number
        context['order_id'] = order_id
        context['pk'] = pk
        context['is_similar_object'] = True
        context['is_evaluator'] = True
        context['show_progress_bar'] = False

        edit_id = self.request.GET.get('edit')

        if edit_id:
            similar_object = get_object_or_404(self.model_similar_object, id=edit_id)
            initial_data = {
                'price': similar_object.price,
                'link': similar_object.link,
                'description': similar_object.description
            }
            context['similar_object_form'] = self.form_class_similar_object(initial=initial_data)
            metadata_initial_data = {meta.key: meta.value for meta in similar_object.metadata.all()}
            context['location_form'] = self.form_class_location(initial=metadata_initial_data)
            context['additional_form'] = self.get_additional_form(obj.object_type, metadata_initial_data)
            context['similar_object_id'] = similar_object.id

        else:
            context['similar_object_form'] = self.form_class_similar_object()
            context['location_form'] = self.form_class_location()
            context['additional_form'] = self.get_additional_form(obj.object_type)
            context['similar_object_id'] = 0

        return context


    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return render(request, self.template_name, context)


    def post(self, request, *args, **kwargs):
        """
        Handles the POST request to create or update a similar object.
        Validates the forms and saves the data if valid.
        """

        context = self.get_context_data(**kwargs)
        location_form = self.form_class_location(request.POST)
        obj = context['object']

        # Determine the additional form based on the object type
        additional_form = self.get_additional_form(obj.object_type, request.POST)
        similar_object_form = self.form_class_similar_object(request.POST) if context['is_similar_object'] else None

        if location_form.is_valid() and (additional_form is None or additional_form.is_valid()) and (similar_object_form is None or similar_object_form.is_valid()):
            edit_id = request.POST.get('edit_id')
            
            if edit_id and edit_id != '0':
                similar_object = get_object_or_404(self.model_similar_object, id=edit_id)
                similar_object.price = similar_object_form.cleaned_data['price']
                similar_object.link = similar_object_form.cleaned_data['link']
                similar_object.description = similar_object_form.cleaned_data['description']

                similar_object.save()
                self.save_metadata(similar_object, location_form)

                if additional_form:
                    self.save_metadata(similar_object, additional_form)
                    
            else:
                similar_object = self.model_similar_object(
                    original_object=context['object'],
                    price=similar_object_form.cleaned_data['price'],
                    link=similar_object_form.cleaned_data['link'],
                    description=similar_object_form.cleaned_data['description']
                )
                similar_object.save()
                self.save_metadata(similar_object, location_form)
                
                if additional_form:
                    self.save_metadata(similar_object, additional_form)

            return redirect(reverse_lazy(self.success_url_name, kwargs={'order_id': context['order_id'], 'pk': context['pk'], 'similar_object_id': similar_object.id}))
        
        return self.form_invalid(location_form, additional_form, similar_object_form)


    def form_invalid(self, location_form, additional_form, similar_object_form):
        context = self.get_context_data()
        context['location_form'] = location_form
        context['additional_form'] = additional_form
        context['similar_object_form'] = similar_object_form
        return self.render_to_response(context)


    def save_metadata(self, similar_object, form):
        for key, value in form.cleaned_data.items():
            SimilarObjectMetadata.objects.update_or_create(
                similar_object=similar_object,
                key=key,
                defaults={'value': value}
            )



            
class EditSimilarObjectDecorationView(LoginRequiredMixin, EvaluatorAccessMixin, UserRoleContextMixin, View):
    """
    This view includes a form for decoration information and updates the metadata for the similar object.
    """

    model = Object
    model_order = Order
    model_user_meta = UserMeta
    template_name = 'edit_evaluation_deco_info.html'
    success_url_name = 'modules.evaluator:edit_similar_object_common_info'
    login_url = 'core.uauth:login'
    redirect_field_name = 'next'

    form_class_decoration = DecorationForm

    def get_object(self):
        order_id = self.kwargs.get('order_id')
        pk = self.kwargs.get('pk')
        return get_object_or_404(self.model, id=pk, order__id=order_id)


    def get_context_data(self, **kwargs):
        context = {}
        order_id = self.kwargs.get('order_id')
        pk = self.kwargs.get('pk')
        similar_object_id = self.kwargs.get('similar_object_id')
        order = get_object_or_404(self.model_order, id=order_id)
        obj = get_object_or_404(self.model, id=pk)
        similar_object = get_object_or_404(SimilarObject, id=similar_object_id)
        client = order.client
        phone_number = self.model_user_meta.get_meta(client, 'phone_num')
        context['order'] = order
        context['object'] = obj
        context['similar_object'] = similar_object
        context['client'] = client
        context['phone_number'] = phone_number
        context['order_id'] = order_id
        context['pk'] = pk
        context['similar_object_id'] = similar_object_id
        context['is_similar_object'] = True
        context['is_evaluator'] = True
        context['show_progress_bar'] = False


        initial_data = {meta.key: meta.value for meta in similar_object.metadata.all()}
        context['decoration_form'] = self.form_class_decoration(initial=initial_data)

        return context


    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return render(request, self.template_name, context)


    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        decoration_form = self.form_class_decoration(request.POST)

        if decoration_form.is_valid():
            similar_object = context['similar_object']
            self.save_metadata(similar_object, decoration_form)

            return redirect(reverse_lazy(self.success_url_name, kwargs={'order_id': context['order_id'], 'pk': context['pk'], 'similar_object_id': similar_object.id}))
        
        return self.form_invalid(decoration_form)


    def form_invalid(self, decoration_form):
        context = self.get_context_data()
        context['decoration_form'] = decoration_form
        return self.render_to_response(context)


    def save_metadata(self, similar_object, form):
        for key, value in form.cleaned_data.items():
            SimilarObjectMetadata.objects.update_or_create(
                similar_object=similar_object,
                key=key,
                defaults={'value': value}
            )


    
class EditSimilarObjectCommonInfoView(LoginRequiredMixin, EvaluatorAccessMixin, UserRoleContextMixin, TemplateView):
    """
    This view includes a form for common information and updates the metadata for the similar object.
    """

    model = Object
    model_order = Order
    model_similar_object = SimilarObject
    model_usermeta = UserMeta
    template_name = 'edit_common_info.html'
    success_url_name = 'modules.evaluator:edit_similar_object_utility_info'
    login_url = 'core.uauth:login'
    redirect_field_name = 'next'

    form_class_common_info = CommonInformationForm

    def get_object(self):
        order_id = self.kwargs.get('order_id')
        pk = self.kwargs.get('pk')
        return get_object_or_404(self.model, id=pk, order__id=order_id)


    def get_context_data(self, **kwargs):
        context = {}
        order_id = self.kwargs.get('order_id')
        pk = self.kwargs.get('pk')
        similar_object_id = self.kwargs.get('similar_object_id')
        order = get_object_or_404(self.model_order, id=order_id)
        obj = get_object_or_404(self.model, id=pk)
        similar_object = get_object_or_404(self.model_similar_object, id=similar_object_id)
        client = order.client
        phone_number = self.model_usermeta.get_meta(client, 'phone_num')
        context['order'] = order
        context['object'] = obj
        context['similar_object'] = similar_object
        context['client'] = client
        context['phone_number'] = phone_number
        context['order_id'] = order_id
        context['pk'] = pk
        context['similar_object_id'] = similar_object_id
        context['is_similar_object'] = True
        context['is_evaluator'] = True
        context['show_progress_bar'] = False


        initial_data = {meta.key: meta.value for meta in similar_object.metadata.all()}
        context['common_info_form'] = self.form_class_common_info(initial=initial_data)

        return context


    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return render(request, self.template_name, context)


    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        common_info_form = self.form_class_common_info(request.POST)

        if common_info_form.is_valid():
            similar_object = context['similar_object']
            self.save_metadata(similar_object, common_info_form)

            return redirect(reverse_lazy(self.success_url_name, kwargs={'order_id': context['order_id'], 'pk': context['pk'], 'similar_object_id': similar_object.id}))
        
        return self.form_invalid(common_info_form)
    

    def form_invalid(self, common_info_form):
        context = self.get_context_data()
        context['common_info_form'] = common_info_form
        return self.render_to_response(context)

    def save_metadata(self, similar_object, form):
        for key, value in form.cleaned_data.items():
            SimilarObjectMetadata.objects.update_or_create(
                similar_object=similar_object,
                key=key,
                defaults={'value': value}
            )



class EditSimilarObjectUtilityInfoView(LoginRequiredMixin, EvaluatorAccessMixin, UserRoleContextMixin, View):
    """
    This view includes a form for utility information and updates the metadata for the similar object.
    """

    model = Object
    model_order = Order
    model_similar_object = SimilarObject
    model_usermeta = UserMeta
    template_name = 'edit_utility_info.html'
    success_url_name = 'modules.evaluator:similar_object_list'
    login_url = 'core.uauth:login'
    redirect_field_name = 'next'

    form_class_utility = UtilityForm

    def get_object(self):
        order_id = self.kwargs.get('order_id')
        pk = self.kwargs.get('pk')
        return get_object_or_404(self.model, id=pk, order__id=order_id)


    def get_context_data(self, **kwargs):
        context = {}
        order_id = self.kwargs.get('order_id')
        pk = self.kwargs.get('pk')
        similar_object_id = self.kwargs.get('similar_object_id')
        order = get_object_or_404(self.model_order, id=order_id)
        obj = get_object_or_404(self.model, id=pk)
        similar_object = get_object_or_404(self.model_similar_object, id=similar_object_id)
        client = order.client
        phone_number = self.model_usermeta.get_meta(client, 'phone_num')
        context['order'] = order
        context['object'] = obj
        context['similar_object'] = similar_object
        context['client'] = client
        context['phone_number'] = phone_number
        context['order_id'] = order_id
        context['pk'] = pk
        context['is_similar_object'] = True
        context['is_evaluator'] = True
        context['similar_object_id'] = similar_object_id
        context['show_progress_bar'] = False


        initial_data = {meta.key: meta.value for meta in similar_object.metadata.all()}
        context['utility_form'] = self.form_class_utility(initial=initial_data)

        return context


    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return render(request, self.template_name, context)


    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        utility_form = self.form_class_utility(request.POST)

        if utility_form.is_valid():
            similar_object = context['similar_object']
            self.save_metadata(similar_object, utility_form)

            return redirect(reverse_lazy(self.success_url_name, kwargs={'order_id': context['order_id'], 'pk': context['pk']}))
        
        return self.form_invalid(utility_form)


    def form_invalid(self, utility_form):
        context = self.get_context_data()
        context['utility_form'] = utility_form
        return self.render_to_response(context)


    def save_metadata(self, similar_object, form):
        for key, value in form.cleaned_data.items():
            SimilarObjectMetadata.objects.update_or_create(
                similar_object=similar_object,
                key=key,
                defaults={'value': value}
            )



class SimilarObjectResultsView(LoginRequiredMixin, EvaluatorAccessMixin, UserRoleContextMixin, TemplateView):
    """
    This view retrieves and displays the search results for similar objects based on the search criteria.
    """

    model_usermeta = UserMeta
    template_name = 'similar_object_results.html'
    login_url = 'core.uauth:login'
    redirect_field_name = 'next'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_id = self.kwargs.get('order_id')
        pk = self.kwargs.get('pk')
        order = get_object_or_404(Order, id=order_id)
        obj = get_object_or_404(Object, id=pk)
        client = order.client
        phone_number = self.model_usermeta.get_meta(client, 'phone_num')
        context['order'] = order
        context['object'] = obj
        context['client'] = client
        context['phone_number'] = phone_number
        context['order_id'] = order_id
        context['pk'] = pk
        context['show_progress_bar'] = SHOW_PROGRESS_BAR
        context['is_evaluator'] = True
        context['current_step'] = 5
        context['total_steps'] = TOTAL_STEPS
        return context




class SimilarObjectListView(LoginRequiredMixin, EvaluatorAccessMixin, UserRoleContextMixin, View):
    """
    This view retrieves and displays the list of similar objects associated with a specific order and object.
    """
    
    template_name = 'similar_object_list.html'
    login_url = 'core.uauth:login'
    redirect_field_name = 'next'
    model_order = Order
    model_object = Object
    model_similar_object = SimilarObject
    model_usermeta = UserMeta

    def get(self, request, *args, **kwargs):
        order_id = self.kwargs.get('order_id')
        pk = self.kwargs.get('pk')
        order = get_object_or_404(self.model_order, id=order_id)
        obj = get_object_or_404(self.model_object, id=pk)
        similar_objects = self.model_similar_object.objects.filter(original_object=obj)

        for similar_object in similar_objects:
            metadata = {meta.key: meta.value for meta in similar_object.metadata.all()}
            similar_object.living_size = metadata.get('living_size', 'N/A')
            similar_object.room_count = metadata.get('room_count', 'N/A')
            similar_object.price = similar_object.price

        client = order.client
        phone_number = self.model_usermeta.get_meta(client, 'phone_num')

        context = {
            'order': order,
            'object': obj,
            'similar_objects': similar_objects,
            'order_id': order_id,
            'pk': pk,
            'show_progress_bar': True,
            'is_evaluator': True,
            'current_step': 5,
            'total_steps': TOTAL_STEPS,
            'client': client,
            'phone_number': phone_number
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        similar_object_id = request.POST.get('similar_object_id')

        if similar_object_id:
            try:
                similar_object = self.model_similar_object.objects.get(id=similar_object_id)
                similar_object.metadata.all().delete()
                similar_object.delete()
                messages.success(request, _('Similar object has been deleted successfully.'))

            except self.model_similar_object.DoesNotExist:
                messages.error(request, _('Similar object not found.'))
                
        return redirect('modules.evaluator:similar_object_list', 
                        order_id=self.kwargs.get('order_id'), 
                        pk=self.kwargs.get('pk'))