"""Indeform OSOM.Codex (Sandbox edition) projects template URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from django.conf.urls.static import static
from django.utils.translation import gettext_lazy as _




urlpatterns = [
    # general
    path('admin/', admin.site.urls),
    path('', include('rarea.urls', namespace='rarea')),

    # core
    path('auth/', include('core.uauth.urls', namespace='core/uauth')),

    # modules
    path('demo/', include('modules.demo.urls', namespace='modules/demo')),

    # orders
    path('orders/', include('modules.orders.urls', namespace='modules/orders')),

    # agency
    path('agency/', include('modules.agency.urls', namespace='modules/agency')),

    # evaluator
    path('evaluator/', include('modules.evaluator.urls', namespace='modules/evaluator')),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


admin.site.site_header = _('ADMIN_AREA_TITLE')
