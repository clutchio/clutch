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

import os
import re

from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.core.urlresolvers import reverse
from django.db import transaction
from django.http import HttpResponseRedirect

from django.contrib.auth.decorators import login_required

from django.contrib import messages

from dashboard.models import App, AppKey, Member, Version, Device
from dashboard.forms import AppForm, MemberForm, DeviceForm, DeleteAppForm
from dashboard.forms import RenameAppForm, ReslugAppForm

from stats.interface import get_screens


def _get_apps(user):
    return App.objects.filter(member__user=user).order_by('id')


@login_required
def home(request):
    apps = _get_apps(request.user)
    return TemplateResponse(request, 'dashboard/home.html', {
        'apps': apps,
    })


@login_required
def devices(request):
    apps = _get_apps(request.user)
    devices = Device.objects.filter(user=request.user).order_by('id')
    return TemplateResponse(request, 'dashboard/devices.html', {
        'apps': apps,
        'devices': devices,
    })


@login_required
def create_device(request):
    form = DeviceForm(request.POST or None)
    if form.is_valid():
        form.save(request.user)
        return HttpResponseRedirect(reverse('dashboard_devices'))
    apps = _get_apps(request.user)
    return TemplateResponse(request, 'dashboard/create_device.html', {
        'form': form,
        'apps': apps,
    })


@login_required
@transaction.commit_on_success
def create_app(request):
    form = AppForm(request.POST or None, user=request.user)
    if form.is_valid():
        app = form.save()
        return HttpResponseRedirect(app.get_quickstart_url())
    apps = _get_apps(request.user)
    return TemplateResponse(request, 'dashboard/create_app.html', {
        'form': form,
        'apps': apps,
    })


@login_required
def app(request, app_slug=None):
    apps = _get_apps(request.user)
    app = get_object_or_404(apps, slug__iexact=app_slug)
    try:
        Member.objects.get(user=request.user, app=app)
    except Member.DoesNotExist:
        return TemplateResponse(request, 'forbidden.html')
    return TemplateResponse(request, 'dashboard/app.html', {
        'apps': apps,
        'app': app,
    })


@login_required
def versions(request, app_slug=None):
    apps = _get_apps(request.user)
    app = get_object_or_404(apps, slug__iexact=app_slug)
    try:
        Member.objects.get(user=request.user, app=app)
    except Member.DoesNotExist:
        return TemplateResponse(request, 'forbidden.html')
    versions = Version.objects.filter(app=app).order_by('-id')
    return TemplateResponse(request, 'dashboard/versions.html', {
        'apps': apps,
        'app': app,
        'versions': versions,
    })


@login_required
def stats(request, app_slug=None, period='month'):
    apps = _get_apps(request.user)
    app = get_object_or_404(apps, slug__iexact=app_slug)
    try:
        Member.objects.get(user=request.user, app=app)
    except Member.DoesNotExist:
        return TemplateResponse(request, 'forbidden.html')
    return TemplateResponse(request, 'dashboard/stats.html', {
        'apps': apps,
        'app': app,
        'period': period,
    })


@login_required
def screen_stats(request, app_slug=None, period='month', screen=None):
    apps = _get_apps(request.user)
    app = get_object_or_404(apps, slug__iexact=app_slug)
    try:
        Member.objects.get(user=request.user, app=app)
    except Member.DoesNotExist:
        return TemplateResponse(request, 'forbidden.html')
    screens = get_screens(app.id)
    return TemplateResponse(request, 'dashboard/screen_stats.html', {
        'apps': apps,
        'app': app,
        'period': period,
        'screens': screens,
        'screen': screen,
    })


@login_required
def settings(request, app_slug=None):
    apps = _get_apps(request.user)
    app = get_object_or_404(apps, slug__iexact=app_slug)
    try:
        user_membership = Member.objects.get(user=request.user, app=app)
    except Member.DoesNotExist:
        return TemplateResponse(request, 'forbidden.html')
    member_form = MemberForm(app=app)
    delete_form = DeleteAppForm()
    rename_form = RenameAppForm()
    reslug_form = ReslugAppForm(user=request.user)
    kind = request.REQUEST.get('kind')
    if kind == 'member':
        member_form = MemberForm(request.POST, app=app)
        if member_form.is_valid():
            member_form.save()
            return HttpResponseRedirect(request.path)
    elif kind == 'delete':
        delete_form = DeleteAppForm(request.POST)
        if delete_form.is_valid():
            app.delete()
            return HttpResponseRedirect(reverse('dashboard_home'))
    elif kind == 'rename':
        rename_form = RenameAppForm(request.POST)
        if rename_form.is_valid():
            app.name = rename_form.cleaned_data['name']
            app.save()
            return HttpResponseRedirect(request.path)
    elif kind == 'reslug':
        reslug_form = ReslugAppForm(request.POST, user=request.user)
        if reslug_form.is_valid():
            app.slug = reslug_form.cleaned_data['slug']
            app.save()
            messages.add_message(request, messages.INFO,
                'IMPORTANT: Make sure to change the short name in your app\'s clutch.plist (listed as ClutchAppShortName)')
            next = reverse('dashboard_settings', args=[app.slug])
            return HttpResponseRedirect(next)
    app_keys = AppKey.objects.filter(app=app).order_by('id')
    members = Member.objects.filter(app=app).order_by('id')
    return TemplateResponse(request, 'dashboard/settings.html', {
        'apps': apps,
        'app': app,
        'app_keys': app_keys,
        'member_form': member_form,
        'delete_form': delete_form,
        'rename_form': rename_form,
        'reslug_form': reslug_form,
        'members': members,
        'user_membership': user_membership,
    })


@login_required
def quickstart(request, app_slug=None):
    apps = _get_apps(request.user)
    app = get_object_or_404(apps, slug__iexact=app_slug)
    try:
        Member.objects.get(user=request.user, app=app)
    except Member.DoesNotExist:
        return TemplateResponse(request, 'forbidden.html')
    app_key = AppKey.objects.filter(
        app=app, status=AppKey.ACTIVE).order_by('-date_created')[0].key
    lslug = app.slug.lower()
    c_src = ''.join([w.title() for w in re.split('[_-]', lslug)])
    c_dir = ('clutch-' + lslug) if '-' in lslug else ('clutch' + lslug)
    clutch_dir = os.path.join(c_src, c_dir)
    return TemplateResponse(request, 'dashboard/quickstart.html', {
        'apps': apps,
        'app': app,
        'app_key': app_key,
        'clutch_dir': clutch_dir,
    })
