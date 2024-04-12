from django.views.generic import TemplateView
from core.mixins import ThemeTemplateMixin

    
class UIGuidelinesView(ThemeTemplateMixin, TemplateView):
    template_name = "ui_guidelines.html"    