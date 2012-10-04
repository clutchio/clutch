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

urlpatterns = patterns('ab.views',
    url(r'^(?P<app_slug>[\w-]+)/experiments/$', 'experiment_list', name='ab_experiment_list'),
    url(r'^(?P<app_slug>[\w-]+)/experiment/(?P<experiment_slug>[\w-]+)/$', 'experiment_detail', name='ab_experiment_detail'),
    url(r'^(?P<app_slug>[\w-]+)/create-experiment/$', 'experiment_create', name='ab_experiment_create'),
    url(r'^(?P<app_slug>[\w-]+)/ab/stats/(?P<experiment_id>\d+)/$', 'experiment_stats', name='ab_experiment_stats'),
    url(r'^(?P<app_slug>[\w-]+)/ab/csv/(?P<experiment_id>\d+)/$', 'experiment_csv', name='ab_experiment_csv'),
    url(r'^(?P<app_slug>[\w-]+)/variation/(?P<variation_id>\d+)/change-name/$', 'variation_change_name', name='ab_variation_change_name'),
    url(r'^(?P<app_slug>[\w-]+)/variation/(?P<variation_id>\d+)/remove/$', 'variation_remove', name='ab_variation_remove'),
    url(r'^(?P<app_slug>[\w-]+)/experiment/(?P<experiment_id>\d+)/create-variation/$', 'variation_create', name='ab_variation_create'),
    url(r'^(?P<app_slug>[\w-]+)/experiment/(?P<experiment_id>\d+)/save-data/$', 'experiment_save_data', name='ab_experiment_save_data'),
    url(r'^(?P<app_slug>[\w-]+)/experiment/(?P<experiment_id>\d+)/delete/$', 'experiment_delete', name='ab_experiment_delete'),
    url(r'^(?P<app_slug>[\w-]+)/ab-quickstart/$', 'quickstart', name='ab_quickstart'),
)