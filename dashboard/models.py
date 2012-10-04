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

from django.db import models
from django.db.models import Q
from django.core.urlresolvers import reverse
from django.utils.timezone import now

from django_ext.utils import datetime_to_timestamp

from django.contrib.auth.models import User

from dashboard.utils import norm_bundle
from dashboard.managers import AppKeyManager


class App(models.Model):
    slug = models.CharField(max_length=50)
    name = models.CharField(max_length=50)
    enabled = models.BooleanField(default=True)
    date_created = models.DateTimeField(default=now)
    custom_user_max = models.IntegerField(null=True, blank=True)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('ab_experiment_list', args=[self.slug])

    def get_quickstart_url(self):
        return reverse('ab_quickstart', args=[self.slug])

    def get_version(self, bundle_version):
        versions = Version.objects.filter(app=self).order_by('-version')
        try:
            bundle = norm_bundle(bundle_version)
            versions = versions.filter(
                Q(max_bundle__lte=bundle) | Q(max_bundle=''),
                Q(min_bundle__gte=bundle) | Q(min_bundle=''),
            )
        except ValueError:
            pass
        try:
            return versions[0].version
        except IndexError:
            return 0


class AppKey(models.Model):
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    STATUSES = (
        (ACTIVE, 'Active'),
        (INACTIVE, 'Inactive'),
    )

    app = models.ForeignKey(App)
    key = models.CharField(max_length=36)
    status = models.CharField(max_length=16, choices=STATUSES, default=ACTIVE)
    date_created = models.DateTimeField(default=now)

    objects = AppKeyManager()

    def __unicode__(self):
        return '%s is the key for app %s' % (self.key, self.app)

    @property
    def status_fmt(self):
        return dict(self.STATUSES)[self.status]

    def data(self):
        return {
            'id': self.id,
            'app': self.app_id,
            'key': self.key,
            'status': self.status,
            'date_created': datetime_to_timestamp(self.date_created),
        }


class DevelopmentMode(models.Model):
    user = models.ForeignKey(User)
    app = models.ForeignKey(App)
    url = models.TextField()
    toolbar = models.BooleanField(default=True)
    date_created = models.DateTimeField(default=now)
    date_updated = models.DateTimeField(default=now)

    def __unicode__(self):
        return '%s is developing on %s' % (self.user, self.app)

    class Meta(object):
        unique_together = (('app', 'user'),)


class Member(models.Model):
    ADMIN = 'admin'
    REGULAR = 'regular'
    LEVELS = (
        (REGULAR, 'Regular User'),
        (ADMIN, 'Administrator'),
    )

    app = models.ForeignKey(App)
    user = models.ForeignKey(User)
    level = models.CharField(max_length=20, choices=LEVELS)
    date_created = models.DateTimeField(default=now)

    def __unicode__(self):
        return '%s is %s %s of %s' % (
            self.user,
            'an' if self.level == self.ADMIN else 'a',
            dict(self.LEVELS)[self.level],
            self.app,
        )

    class Meta(object):
        unique_together = (('app', 'user'),)

    @property
    def is_admin(self):
        return self.level == self.ADMIN


class Version(models.Model):
    app = models.ForeignKey(App)
    min_bundle = models.CharField(max_length=20, default='', blank=True)
    max_bundle = models.CharField(max_length=20, default='', blank=True)
    version = models.IntegerField()
    date_created = models.DateTimeField(default=now)

    def __unicode__(self):
        return '%s version %s' % (self.app, self.version)

    class Meta(object):
        unique_together = (('app', 'version'),)


class Device(models.Model):
    user = models.ForeignKey(User)
    udid = models.CharField(max_length=32)
    name = models.TextField(null=False, blank=True, default='')
    primary = models.BooleanField()
    date_created = models.DateTimeField(default=now)

    def __unicode__(self):
        return '%s\'s device "%s" udid:%s' % (
            self.user,
            self.name,
            self.udid,
        )
