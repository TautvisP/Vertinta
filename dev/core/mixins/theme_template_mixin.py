import logging

from typing import Callable
from django.core.exceptions import ImproperlyConfigured
from django.template import TemplateDoesNotExist, loader


class ThemeTemplateMixin:
    """
    Mixin for Django views that allows them to load theme specific templates.

    This mixin provides a mechanism to render templates based on the currently
    selected theme. Since Django HTML templates do not support string interpolation with 
    "include" and "extend" statements, it supplies paths to layout and module menu
    templates through the context data.

    Attributes:
        template_name (str): The base filename of the template. It should not be a
                             full path to the template, just the name.
    
        area_app_name (str): App name whose generic templates are used (e.g. layouts, menus) by other modules.
        
        layout_template_path (str): Path to the layout template, relative to the templates directory within 
                                    the area app, for example, "layout.html".

        nav_template_path (str): Path to the module menu template, relative to the module app tempaltes directory.

        nav_template_wrapper_path (str): Path to the module menu wrapper template, relative to the area app templates directory.
    """

    template_name: str = None
    area_app_name: str = 'rarea'
    layout_template_path: str = 'layout.html'
    menu_template_path: str = 'components/menu.html'
    menu_template_wrapper_path: str = 'shared/menu_wrapper.html'

    def get_theme_name(self) -> str:
        """
            Returns the theme name from user preferences. If the theme attribute
            value could not be read, "default" is returned instead.

            Returns:
                str: Theme name from preferences or "default".
        """
        logger = logging.getLogger(__name__)

        if not self.request.user or not hasattr(self.request.user, 'preferences'):
            logger.warn('User is not authenticated or user preferences are not configured, will use "default" as a theme name.')
            return 'default'

        return self.request.user.preferences.get('theme', 'default')

    def get_themed_path_builder(self, app_name: str, template_path: str) -> Callable[[str], str]:
        """
            Returns a closure function with the given app name and template path to create
            a path to the themed template file.

            Returns:
                Callable[[str], str]: Template path builder function.
        """
        return lambda theme: f'{app_name}/{theme}/{template_path}'

    def get_context_data(self, **kwargs) -> object:
        context = super().get_context_data(**kwargs)

        templates = {
            'layout_template': self.get_themed_path_builder(
                self.area_app_name,
                self.layout_template_path,
            ),
            'menu_template': self.get_themed_path_builder(
                self.request.resolver_match.app_name,
                self.menu_template_path,
            ),
            'menu_wrapper_template': self.get_themed_path_builder(
                self.area_app_name,
                self.menu_template_wrapper_path,
            ),
        }

        self.theme_name = self.get_theme_name()

        for context_key, themed_template_getter in templates.items():
            try:
                template_path = themed_template_getter(self.theme_name)
                loader.get_template(template_path)
                context[context_key] = template_path
            except TemplateDoesNotExist:
                context[context_key] = themed_template_getter('default')
    
        context['theme'] = self.theme_name
        return context

    def get_template_names(self) -> list[str]:
        """
        Builds a list of template paths based on the user's selected theme. Will fallback
        to templates from the `<APP_NAME>/templates/default` folder if themed template does not exist.

        Raises:
            ImproperlyConfigured: If 'template_name' attribute is not set.

        Returns:
            list: A list of template paths to attempt loading.
        """
        if not self.template_name:
            raise ImproperlyConfigured('ThemeTemplateMixin requires "template_name" attribute to be set.')

        app_name = self.request.resolver_match.app_name
        template_path = f'{app_name}/{self.theme_name}/{self.template_name}'

        try:
            loader.get_template(template_path)
            return [template_path]
        except TemplateDoesNotExist:
            return [f'{app_name}/default/{self.template_name}']