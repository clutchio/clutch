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


class Log(models.Model):
    uuid = models.CharField(max_length=62, primary_key=True, unique=True, default=lambda: str(uuid.uuid1()))
    timestamp = models.FloatField()
    action = models.CharField(max_length=20)
    data = models.TextField()
    udid = models.CharField(max_length=32)
    api_version = models.CharField(max_length=6)
    app_version = models.IntegerField()
    bundle_version = models.CharField(max_length=20)
    app_key = models.CharField(max_length=36)
    platform = models.CharField(max_length=12, default='iOS')

    class Meta(object):
        unique_together = (('timestamp', 'udid'),)

    def __unicode__(self):
        return str((
            self.timestamp,
            self.action,
            self.data,
            self.udid,
            self.api_version,
            self.app_version,
            self.bundle_version,
            self.app_key,
        ))


class ViewHour(models.Model):
    app_id = models.IntegerField()
    timestamp = models.DateTimeField()
    views = models.IntegerField()
    platform = models.CharField(max_length=12, default='iOS')

    class Meta(object):
        unique_together = (('app_id', 'timestamp', 'platform'),)

    def __unicode__(self):
        return str((self.app_id, self.timestamp, self.views, self.platform))


class ViewSlugHour(models.Model):
    app_id = models.IntegerField()
    timestamp = models.DateTimeField()
    slug = models.TextField()
    views = models.IntegerField()
    platform = models.CharField(max_length=12, default='iOS')

    class Meta(object):
        unique_together = (('app_id', 'timestamp', 'slug', 'platform'),)

    def __unicode__(self):
        return str((self.app_id, self.timestamp, self.slug, self.views,
            self.platform))


class ViewDay(models.Model):
    app_id = models.IntegerField()
    timestamp = models.DateTimeField()
    views = models.IntegerField()
    platform = models.CharField(max_length=12, default='iOS')

    class Meta(object):
        unique_together = (('app_id', 'timestamp', 'platform'),)

    def __unicode__(self):
        return str((self.app_id, self.timestamp, self.views, self.platform))


class ViewSlugDay(models.Model):
    app_id = models.IntegerField()
    timestamp = models.DateTimeField()
    slug = models.TextField()
    views = models.IntegerField()
    platform = models.CharField(max_length=12, default='iOS')

    class Meta(object):
        unique_together = (('app_id', 'timestamp', 'slug', 'platform'),)

    def __unicode__(self):
        return str((self.app_id, self.timestamp, self.slug, self.views,
            self.platform))


class ViewMonth(models.Model):
    app_id = models.IntegerField()
    timestamp = models.DateTimeField()
    views = models.IntegerField()
    platform = models.CharField(max_length=12, default='iOS')

    class Meta(object):
        unique_together = (('app_id', 'timestamp', 'platform'),)

    def __unicode__(self):
        return str((self.app_id, self.timestamp, self.views, self.platform))


class ViewSlugMonth(models.Model):
    app_id = models.IntegerField()
    timestamp = models.DateTimeField()
    slug = models.TextField()
    views = models.IntegerField()
    platform = models.CharField(max_length=12, default='iOS')

    class Meta(object):
        unique_together = (('app_id', 'timestamp', 'slug', 'platform'),)

    def __unicode__(self):
        return str((self.app_id, self.timestamp, self.slug, self.views,
            self.platform))


class ViewYear(models.Model):
    app_id = models.IntegerField()
    timestamp = models.DateTimeField()
    views = models.IntegerField()
    platform = models.CharField(max_length=12, default='iOS')

    class Meta(object):
        unique_together = (('app_id', 'timestamp', 'platform'),)

    def __unicode__(self):
        return str((self.app_id, self.timestamp, self.views, self.platform))


class ViewSlugYear(models.Model):
    app_id = models.IntegerField()
    timestamp = models.DateTimeField()
    slug = models.TextField()
    views = models.IntegerField()
    platform = models.CharField(max_length=12, default='iOS')

    class Meta(object):
        unique_together = (('app_id', 'timestamp', 'slug', 'platform'),)

    def __unicode__(self):
        return str((self.app_id, self.timestamp, self.slug, self.views,
            self.platform))


class UniqueHour(models.Model):
    app_id = models.IntegerField()
    timestamp = models.DateTimeField()
    udid = models.CharField(max_length=32)
    new = models.BooleanField(default=True)
    platform = models.CharField(max_length=12, default='iOS')

    class Meta(object):
        unique_together = (('app_id', 'timestamp', 'udid', 'platform'),)

    def __unicode__(self):
        return str((self.app_id, self.timestamp, self.udid, self.new,
            self.platform))


class UniqueDay(models.Model):
    app_id = models.IntegerField()
    timestamp = models.DateTimeField()
    udid = models.CharField(max_length=32)
    new = models.BooleanField(default=True)
    platform = models.CharField(max_length=12, default='iOS')

    class Meta(object):
        unique_together = (('app_id', 'timestamp', 'udid', 'platform'),)

    def __unicode__(self):
        return str((self.app_id, self.timestamp, self.udid, self.new,
            self.platform))


class UniqueMonth(models.Model):
    app_id = models.IntegerField()
    timestamp = models.DateTimeField()
    udid = models.CharField(max_length=32)
    new = models.BooleanField(default=True)
    platform = models.CharField(max_length=12, default='iOS')

    class Meta(object):
        unique_together = (('app_id', 'timestamp', 'udid', 'platform'),)

    def __unicode__(self):
        return str((self.app_id, self.timestamp, self.udid, self.new,
            self.platform))


class UniqueYear(models.Model):
    app_id = models.IntegerField()
    timestamp = models.DateTimeField()
    udid = models.CharField(max_length=32)
    new = models.BooleanField(default=True)
    platform = models.CharField(max_length=12, default='iOS')

    class Meta(object):
        unique_together = (('app_id', 'timestamp', 'udid', 'platform'),)

    def __unicode__(self):
        return str((self.app_id, self.timestamp, self.udid, self.new,
            self.platform))


class UniqueAllTime(models.Model):
    app_id = models.IntegerField()
    timestamp = models.DateTimeField(default=now)
    udid = models.CharField(max_length=32)
    platform = models.CharField(max_length=12, default='iOS')

    class Meta(object):
        unique_together = (('app_id', 'udid', 'platform'),)

    def __unicode__(self):
        return str((self.app_id, self.udid, self.platform))
