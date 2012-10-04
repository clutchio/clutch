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

from stats.models import Log, ViewHour, ViewSlugHour, ViewDay, ViewSlugDay
from stats.models import ViewMonth, ViewSlugMonth, ViewYear, ViewSlugYear
from stats.models import UniqueHour, UniqueDay, UniqueMonth, UniqueYear
from stats.models import UniqueAllTime

admin.site.register((Log, ViewHour, ViewSlugHour, ViewDay, ViewSlugDay,
    ViewMonth, ViewSlugMonth, ViewYear, ViewSlugYear, UniqueHour, UniqueDay,
    UniqueMonth, UniqueYear, UniqueAllTime))
