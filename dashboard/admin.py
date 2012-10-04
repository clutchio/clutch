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

from dashboard.models import App, AppKey, DevelopmentMode, Member, Version
from dashboard.models import Device


class AppAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'enabled', 'custom_user_max', 'date_created')
    list_filter = ('enabled',)
    date_hierarchy = 'date_created'
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('-date_created',)
    search_fields = ('name', 'slug')


class DevelopmentModeAdmin(admin.ModelAdmin):
    list_display = ('user', 'app', 'url', 'toolbar', 'date_created', 'date_updated')
    date_hierarchy = 'date_updated'
    ordering = ('-date_updated',)
    raw_id_fields = ('app', 'user')


class AppKeyAdmin(admin.ModelAdmin):
    list_display = ('app', 'key')
    date_hierarchy = 'date_created'
    ordering = ('-date_created',)
    raw_id_fields = ('app',)


class MemberAdmin(admin.ModelAdmin):
    list_display = ('app', 'user', 'level', 'date_created')
    date_hierarchy = 'date_created'
    ordering = ('-date_created',)
    raw_id_fields = ('user', 'app')


class VersionAdmin(admin.ModelAdmin):
    list_display = ('app', 'min_bundle', 'max_bundle', 'version',
        'date_created')
    date_hierarchy = 'date_created'
    ordering = ('-date_created',)
    raw_id_fields = ('app',)


class DeviceAdmin(admin.ModelAdmin):
    list_display = ('user', 'udid', 'primary', 'name')
    date_hierarchy = 'date_created'
    ordering = ('-date_created',)
    raw_id_fields = ('user',)


admin.site.register(App, AppAdmin)
admin.site.register(AppKey, AppKeyAdmin)
admin.site.register(DevelopmentMode, DevelopmentModeAdmin)
admin.site.register(Member, MemberAdmin)
admin.site.register(Version, VersionAdmin)
admin.site.register(Device, DeviceAdmin)
