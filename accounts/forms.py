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

from django import forms

from django.contrib.auth.models import User


class LoginForm(forms.Form):
    username = forms.CharField(max_length=75, label='Username')
    password = forms.CharField(widget=forms.PasswordInput(render_value=False), label='Password')

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.user = None

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        # Short circuit if they haven't entered in their password
        if not username or not password:
            return self.cleaned_data
        # User by username
        try:
            self.user = User.objects.get(username__iexact=username)
        except User.DoesNotExist:
            pass
        # User by email
        try:
            self.user = User.objects.get(email__iexact=username)
        except User.DoesNotExist:
            pass
        if self.user is None or not self.user.check_password(password):
            raise forms.ValidationError(u'Invalid username and/or password')
        return self.cleaned_data


class AccountForm(forms.Form):
    email = forms.EmailField(max_length=75, label='E-Mail')
    password = forms.CharField(required=False, widget=forms.PasswordInput(render_value=False), label='New Password')

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(AccountForm, self).__init__(*args, **kwargs)
        self.initial.update({
            'email': self.user.email,
        })

    def save(self):
        self.user.email = self.cleaned_data['email']
        password = self.cleaned_data.get('password', '').strip()
        if password:
            self.user.set_password(password)
        self.user.save(force_update=True)


class RegistrationForm(forms.Form):
    username = forms.RegexField(
        regex=r'^\w+$',
        max_length=30,
        error_messages={
            'invalid': 'Valid usernames can only have letters, numbers, dashes, and underscores.',
        },
        label='Username'
    )
    email = forms.EmailField(max_length=75, label='E-Mail')
    password = forms.CharField(widget=forms.PasswordInput(render_value=False), label='Password')
    email_updates = forms.BooleanField(required=False, label='Would you like to receive occasional e-mail updates?')

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super(RegistrationForm, self).__init__(*args, **kwargs)

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            User.objects.get(username__iexact=username)
            raise forms.ValidationError(u'Username is already taken.')

        except User.DoesNotExist:
            pass
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        try:
            User.objects.get(email__iexact=email)
            raise forms.ValidationError(u'E-mail address is already taken.')
        except User.DoesNotExist:
            pass
        return email

    def save(self):
        user = User.objects.create_user(
            self.cleaned_data['username'],
            self.cleaned_data['email'],
            self.cleaned_data['password']
        )
        return user
