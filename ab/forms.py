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

from ab.models import Experiment

HAS_DATA_CHOICES = (
    ('f', 'Normal'),
    ('t', 'Data-Driven'),
)


class ExperimentForm(forms.Form):
    name = forms.CharField(max_length=62, required=True)
    slug = forms.RegexField(label='Short Name', max_length=62, required=True,
        regex=r'^[\w-]+$',
        help_text='This short name will be used in your code to reference this experiment.')
    has_data = forms.ChoiceField(label='Experiment Type', required=True,
        choices=HAS_DATA_CHOICES)

    def __init__(self, *args, **kwargs):
        self.app = kwargs.pop('app')
        self.user = kwargs.pop('user')
        super(ExperimentForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder = ['has_data', 'name', 'slug']

    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        if slug is None:
            return slug
        try:
            Experiment.objects.get(app=self.app, slug__iexact=slug)
            raise forms.ValidationError('Experiment with short name "%s" already exists, please choose another one.' % (slug,))
        except Experiment.DoesNotExist:
            pass
        return slug

    def save(self):
        return Experiment.objects.create(
            app=self.app,
            name=self.cleaned_data['name'],
            slug=self.cleaned_data['slug'],
            has_data=self.cleaned_data['has_data'] == 't',
        )
