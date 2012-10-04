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

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('dashboard.views',
    url(r'^(?P<app_slug>[\w-]+)/$', 'stats', name='dashboard_app'),
    url(r'^(?P<app_slug>[\w-]+)/versions/$', 'versions', name='dashboard_versions'),
    url(r'^(?P<app_slug>[\w-]+)/stats/$', 'stats', name='dashboard_stats'),
    url(r'^(?P<app_slug>[\w-]+)/quickstart/$', 'quickstart', name='dashboard_quickstart'),
    url(r'^(?P<app_slug>[\w-]+)/stats/(?P<period>today|month|months|alltime)/$', 'stats', name='dashboard_stats'),
    url(r'^(?P<app_slug>[\w-]+)/screen-stats/$', 'screen_stats', name='dashboard_screen_stats'),
    url(r'^(?P<app_slug>[\w-]+)/screen-stats/(?P<period>today|month|months|alltime)/$', 'screen_stats', name='dashboard_screen_stats'),
    url(r'^(?P<app_slug>[\w-]+)/screen-stats/(?P<period>today|month|months|alltime)/(?P<screen>[\w-]+)/$', 'screen_stats', name='dashboard_screen_stats'),
    url(r'^(?P<app_slug>[\w-]+)/settings/$', 'settings', name='dashboard_settings'),
)
