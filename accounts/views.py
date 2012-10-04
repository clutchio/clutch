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

from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse

from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import get_backends
from django.contrib.auth.decorators import login_required

from django.contrib import messages

from dashboard.models import App

from accounts.forms import LoginForm, RegistrationForm, AccountForm

from stats.interface import get_current_monthly_user_count


def _backend_hackend(request, user):
    backend = get_backends()[0]
    user.backend = '%s.%s' % (backend.__module__,
        backend.__class__.__name__)
    auth_login(request, user)


def login(request):
    login_form = LoginForm(request.POST or None)
    if login_form.is_valid():
        _backend_hackend(request, login_form.user)
        return HttpResponseRedirect(request.REQUEST.get('next', '/'))
    context = {
        'login_form': login_form,
    }
    return TemplateResponse(request, 'accounts/login.html', context)


def register(request):
    registration_form = RegistrationForm(request.POST or None, request=request)
    if registration_form.is_valid():
        user = registration_form.save()
        _backend_hackend(request, user)

        return HttpResponseRedirect(request.REQUEST.get('next', '/'))

    context = {
        'registration_form': registration_form,
        'months': range(1, 13),
        'years': range(2011, 2036),
    }
    return TemplateResponse(request, 'accounts/register.html', context)


def logout(request):
    auth_logout(request)
    return TemplateResponse(request, 'accounts/logout.html')


@login_required
def accounts(request):
    if request.method == 'POST':
        account_form = AccountForm(request.POST, user=request.user)
        if account_form.is_valid():
            account_form.save()
            messages.add_message(request, messages.INFO,
                'Updated account details saved successfully!')
            return HttpResponseRedirect(request.path)
    else:
        account_form = AccountForm(user=request.user)

    apps = []
    for app in App.objects.filter(member__user=request.user):
        app.active = get_current_monthly_user_count(app)
        apps.append(app)

    context = {
        'apps': apps,
        'account_form': account_form,
    }
    return TemplateResponse(request, 'accounts/accounts.html', context)
