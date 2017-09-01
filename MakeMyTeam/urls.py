"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
	url(r'^', include('mkmt.urls')),
    url(r'break_my_team', include('mkmt.urls')),
    url(r'mcr_list_generator', include('mkmt.urls')),
    url(r'Pokemon_data', include('mkmt.urls')),
    url(r'custom_generator', include('mkmt.urls')),
    url(r'partner_finder', include('mkmt.urls')),
    url(r'core_builder', include('mkmt.urls')),
    url(r'team_generator', include('mkmt.urls')),
    url(r'replacement_suggestor', include('mkmt.urls')),
    url(r'team_completer', include('mkmt.urls')),
    url(r'counterteam_generator', include('mkmt.urls')),
    url(r'team_comparer', include('mkmt.urls')),
    url(r'check_map', include('mkmt.urls')),
    url(r'set_usage_stats', include('mkmt.urls')),
    url(r'how_to_update', include('mkmt.urls')),
    url(r'credits', include('mkmt.urls')),
]

from <app> import settings
urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
    )