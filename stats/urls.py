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

urlpatterns = patterns('stats.views',
    url(r'^actives/(?P<app_id>\d+)/(?P<period>today|month|months|alltime)\.json$', 'actives', name='stats_actives'),
    url(r'^new-users/(?P<app_id>\d+)/(?P<period>today|month|months|alltime)\.json$', 'new_users', name='stats_new_users'),
    url(r'^screen-views/(?P<screen>[\w-]+)/(?P<app_id>\d+)/(?P<period>today|month|months|alltime)\.json$', 'screen_views', name='stats_screen_views'),
    url(r'^views/(?P<app_id>\d+)/(?P<period>today|month|months|alltime)\.json$', 'views', name='stats_views'),
    url(r'^total-users/(?P<app_id>\d+)/(?P<period>today|month|months|alltime)\.json$', 'total_users', name='stats_total_users'),
    url(r'^quick/(?P<app_id>\d+)/(?P<period>today|month|months|alltime)\.json$', 'quick', name='stats_quick'),
)
