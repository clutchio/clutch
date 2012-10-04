# Copyright 2012 Twitter
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from django.conf.urls.defaults import patterns, include, handler404, handler500
repr(handler404)  # Placate PyFlakes
repr(handler500)  # Placate PyFlakes
from django.conf.urls.defaults import url

from django.contrib import admin

from django.contrib.staticfiles.urls import staticfiles_urlpatterns

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^/?$', 'clutch.views.index', name='index'),

    (r'^app/', include('dashboard.urls')),
    url(r'^apps/$', 'dashboard.views.home', name='dashboard_home'),
    url(r'^apps/create/$', 'dashboard.views.create_app', name='dashboard_create_app'),
    url(r'^devices/$', 'dashboard.views.devices', name='dashboard_devices'),
    url(r'^devices/create/$', 'dashboard.views.create_device', name='dashboard_create_device'),
    url(r'^action/(?P<action>[\w-]+)\.json', 'dashboard.actions.dispatch', name='dashboard_actions'),

    url(r'^app/', include('ab.urls')),

    (r'^stats/', include('stats.urls')),

    url(r'^login/$', 'accounts.views.login', name='login'),
    url(r'^register/$', 'accounts.views.register', name='register'),
    url(r'^logout/$', 'accounts.views.logout', name='logout'),
    (r'^accounts/', include('accounts.urls')),

    url(r'^error/404/$', 'django.views.generic.simple.direct_to_template', {'template': '404.html'}),
    url(r'^error/500/$', 'django.views.generic.simple.direct_to_template', {'template': '500.html'}),

    url(r'^health-check/$', 'django.views.generic.simple.direct_to_template', {'template': 'simple/healthcheck.html'}),

    url(r'^admin/login/(?P<username>[\w-]+)/$', 'admin_ext.views.admin_login', name='admin_login'),
    url(r'^admin/metrics/$', 'admin_ext.views.metrics', name='admin_metrics'),
    (r'^admin/', include(admin.site.urls)),
) + staticfiles_urlpatterns()
