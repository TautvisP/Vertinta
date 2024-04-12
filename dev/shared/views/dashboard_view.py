import json
from django.conf import settings
from django.views.generic import TemplateView
from core.mixins import ThemeTemplateMixin



class DashboardView(ThemeTemplateMixin, TemplateView):
    template_name = 'dashboard.html'
    module = 'osomjs'


    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)
        
        readme_file = settings.BASE_DIR / 'modules' / self.module / 'about.json' # fix needed to acce

        print(readme_file)

        if readme_file.is_file():
            with open(readme_file, 'r') as f:
                try:
                    module_notes = json.load(f)
                    context['module'] = module_notes
                except ValueError:
                    print('Module "module_notes" JSON file loading failed.')

        return context

