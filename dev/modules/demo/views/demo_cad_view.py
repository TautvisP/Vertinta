from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin


    
class CADView(TemplateView, LoginRequiredMixin):
    template_name = "modules/demo/cad.html"
