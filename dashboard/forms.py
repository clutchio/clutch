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

import uuid

from django import forms

from django.contrib.auth.models import User

from dashboard.models import App, AppKey, Member, Device


class AppForm(forms.Form):
    name = forms.CharField(max_length=50, required=True)
    slug = forms.RegexField(max_length=50, label='Short Name', regex=r'^[\w-]+$', required=True)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(AppForm, self).__init__(*args, **kwargs)

    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        if slug is None:
            return slug
        try:
            App.objects.filter(member__user=self.user).get(slug__iexact=slug)
            raise forms.ValidationError('App with slug "%s" already exists, please choose another one.' % (slug,))
        except App.DoesNotExist:
            pass
        return slug

    def save(self):
        app = App.objects.create(
            name=self.cleaned_data['name'],
            slug=self.cleaned_data['slug']
        )
        Member.objects.create(
            app=app,
            user=self.user,
            level=Member.ADMIN
        )
        AppKey.objects.create(
            app=app,
            key=str(uuid.uuid4())
        )
        return app


class DeviceForm(forms.Form):
    name = forms.CharField(max_length=100, required=True, help_text='(Can be anything, this is to help you remember)')
    udid = forms.CharField(max_length=32, label='Identifier', required=True)

    def save(self, user):
        primary = Device.objects.filter(user=user).count() == 0
        device = Device.objects.create(
            user=user,
            name=self.cleaned_data['name'],
            udid=self.cleaned_data['udid'],
            primary=primary
        )
        return device


class MemberForm(forms.Form):
    username = forms.RegexField(
        regex=r'^\w+$',
        max_length=30,
        error_messages={
            'invalid': 'Valid usernames can only have letters, numbers, dashes, and underscores.',
        },
        label='Username',
        required=True
    )
    level = forms.ChoiceField(Member.LEVELS, label='Membership Level', required=True)

    def __init__(self, *args, **kwargs):
        app = kwargs.pop('app', None)
        if app is None:
            raise ValueError('Must provide an app to MemberForm')
        self.app = app
        super(MemberForm, self).__init__(*args, **kwargs)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username is None:
            return username
        try:
            self.user = User.objects.get(username__iexact=username)
        except User.DoesNotExist:
            raise forms.ValidationError('User "%s" does not exist.' % (username,))
        try:
            Member.objects.get(user=self.user, app=self.app)
            raise forms.ValidationError('User "%s" is already added to this app.' % (username,))
        except Member.DoesNotExist:
            pass
        return username

    def save(self):
        return Member.objects.create(
            user=self.user,
            app=self.app,
            level=self.cleaned_data['level']
        )


class DeleteAppForm(forms.Form):
    confirm = forms.BooleanField(label='I acknowledge that this action is permanent and cannot be undone:')


class RenameAppForm(forms.Form):
    name = forms.CharField(max_length=50, required=True)


class ReslugAppForm(forms.Form):
    slug = forms.RegexField(max_length=50, label='Short Name', regex=r'^[\w-]+$', required=True)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(ReslugAppForm, self).__init__(*args, **kwargs)

    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        if slug is None:
            return slug
        try:
            App.objects.filter(member__user=self.user).get(slug__iexact=slug)
            raise forms.ValidationError('App with slug "%s" already exists, please choose another one.' % (slug,))
        except App.DoesNotExist:
            pass
        return slug
