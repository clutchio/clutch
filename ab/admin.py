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

from django.contrib import admin

from ab.models import Log, Trial, UniqueMonth, Experiment, Variation


class LogAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'timestamp', 'udid', 'api_version', 'app_version',
        'bundle_version', 'app_key', 'platform')


class TrialAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'udid', 'app_id', 'experiment_id', 'date_started',
        'date_completed', 'goal_reached')
    list_filter = ('goal_reached',)
    date_hierarchy = 'date_created'
    ordering = ('-date_created',)


class UniqueMonthAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'udid', 'app_id', 'month', 'date_created')
    date_hierarchy = 'date_created'
    ordering = ('-date_created',)


class ExperimentAdmin(admin.ModelAdmin):
    list_display = ('app', 'name', 'slug', 'has_data', 'enabled',
        'date_created')
    list_filter = ('has_data', 'enabled')
    date_hierarchy = 'date_created'
    ordering = ('-date_created',)
    search_fields = ('name', 'slug')
    raw_id_fields = ('app',)


class VariationAdmin(admin.ModelAdmin):
    list_display = ('experiment', 'weight', 'num', 'name', 'date_created')
    list_filter = ('num',)
    date_hierarchy = 'date_created'
    ordering = ('-date_created',)
    raw_id_fields = ('experiment',)


admin.site.register(Log, LogAdmin)
admin.site.register(Trial, TrialAdmin)
admin.site.register(UniqueMonth, UniqueMonthAdmin)
admin.site.register(Experiment, ExperimentAdmin)
admin.site.register(Variation, VariationAdmin)
