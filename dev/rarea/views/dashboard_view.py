import json
from django.apps import apps
from django.conf import settings
from django.views.generic import TemplateView
#from django.core.urlresolvers import resolve
from core.mixins import ThemeTemplateMixin



class DashboardView(ThemeTemplateMixin, TemplateView):
    """
    Generic view for module description and release notes rendering.
    """

    template_name = 'dashboard.html'

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)

        if "app_name" in kwargs:
            app_cfg = apps.get_app_config(kwargs["app_name"])

            if app_cfg is not None:
                app_path = app_cfg.name.replace('.', '/')
                json_path = settings.BASE_DIR / app_path / 'about.json'

                if json_path.is_file():
                    with open(json_path, 'r') as f:
                        try:
                            context['module'] = json.load(f)
                        except ValueError:
                            print('JSON loading failed')

        return context