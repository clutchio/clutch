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

from django.db import models
from django.utils.timezone import now

from dashboard.models import App


class Log(models.Model):
    uuid = models.CharField(max_length=62, primary_key=True, unique=True)
    timestamp = models.FloatField()
    data = models.TextField()
    udid = models.CharField(max_length=32)
    api_version = models.CharField(max_length=6)
    app_version = models.IntegerField()
    bundle_version = models.CharField(max_length=20)
    app_key = models.CharField(max_length=36)
    platform = models.CharField(max_length=12, default='iOS')
    action = models.CharField(max_length=36, null=True)  # Doesn't need to be null=True

    class Meta(object):
        unique_together = (('timestamp', 'udid'),)

    def __unicode__(self):
        return str((
            self.timestamp,
            self.data,
            self.udid,
            self.api_version,
            self.app_version,
            self.bundle_version,
            self.app_key,
        ))


class Trial(models.Model):
    uuid = models.CharField(max_length=62, primary_key=True, unique=True,
        default=lambda: str(uuid.uuid1()))
    udid = models.CharField(max_length=32)
    app_id = models.PositiveIntegerField()
    choice = models.IntegerField(default=1)
    experiment_id = models.PositiveIntegerField()
    date_created = models.DateTimeField(default=now)
    date_started = models.DateTimeField(default=now)
    date_completed = models.DateTimeField(null=True, default=None)
    goal_reached = models.BooleanField(default=False)

    class Meta(object):
        unique_together = (('udid', 'experiment_id'),)


class UniqueMonth(models.Model):
    uuid = models.CharField(max_length=62, primary_key=True, unique=True,
        default=lambda: str(uuid.uuid1()))
    app_id = models.PositiveIntegerField()
    udid = models.CharField(max_length=32)
    month = models.DateTimeField()
    date_created = models.DateTimeField(default=now)

    class Meta(object):
        unique_together = (('app_id', 'month', 'udid'),)


class Experiment(models.Model):
    app = models.ForeignKey(App)
    name = models.CharField(max_length=62)
    slug = models.CharField(max_length=62)
    has_data = models.BooleanField()
    enabled = models.BooleanField(default=True)
    num_choices = models.IntegerField(default=0)
    date_created = models.DateTimeField(default=now)

    class Meta(object):
        unique_together = (('app', 'slug'),)

    def __unicode__(self):
        return self.name


class Variation(models.Model):
    experiment = models.ForeignKey(Experiment)
    weight = models.FloatField()
    num = models.IntegerField(default=1)  # A? B? C?
    name = models.CharField(max_length=62)
    data = models.TextField(blank=True, default='')
    date_created = models.DateTimeField(default=now)

    class Meta(object):
        unique_together = (('experiment', 'num'),)

    def __unicode__(self):
        return self.name

    @property
    def letter(self):
        return 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'[self.num - 1]
