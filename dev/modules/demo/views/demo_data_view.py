from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from modules.demo.models import Product




class DataView(CreateView, LoginRequiredMixin):
    template_name = 'modules/demo/data.html'
    model = Product
    fields = ['code', 'title', 'stock']
    success_url = reverse_lazy('modules/demo:data')


    def get_context_data(self, **kwargs):
        kwargs['object_list'] = Product.objects.order_by('code')
        print(kwargs['object_list'])
        return super(DataView, self).get_context_data(**kwargs)    


    def form_valid(self, form):
        form.save()
        return super().form_valid(form)