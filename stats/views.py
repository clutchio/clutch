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

from django.utils.timezone import now

from django_ext.http import JSONResponse
from django_ext.utils import datetime_to_timestamp

from stats.interface import get_active_users, get_views, get_total_users
from stats.interface import get_total_user_count, get_active_user_count
from stats.interface import get_new_user_count, get_view_count
from stats.interface import get_screen_views, PERIODS


def _prepare_json(stats, period):
    if period == PERIODS.TODAY:
        display = lambda item: item.strftime('%I%p UTC').lstrip('0')
    else:
        display = lambda item: item.strftime('%b %d')
    return [
        {
            'timestamp': datetime_to_timestamp(item['timestamp']),
            'timestamp_fmt': display(item['timestamp']),
            'stat': item['stat'],
            'show': item['timestamp'] <= now(),
        }
        for item in stats
    ]


def actives(request, app_id=None, period=None):
    app_id = int(app_id)
    period = getattr(PERIODS, period.upper())
    stats = get_active_users(app_id, period, platform='iOS')
    stats_prev = get_active_users(app_id, period, prev=True, platform='iOS')
    android_stats = get_active_users(app_id, period, platform='Android')
    android_stats_prev = get_active_users(app_id, period, prev=True,
        platform='Android')
    return JSONResponse(request, {
        'stats': _prepare_json(stats, period),
        'stats_prev': _prepare_json(stats_prev, period),
        'android_stats': _prepare_json(android_stats, period),
        'android_stats_prev': _prepare_json(android_stats_prev, period),
        'unit': 'User',
    })


def new_users(request, app_id=None, period=None):
    app_id = int(app_id)
    period = getattr(PERIODS, period.upper())
    stats = get_active_users(app_id, period, new_only=True, platform='iOS')
    stats_prev = get_active_users(app_id, period, new_only=True, prev=True,
        platform='iOS')
    android_stats = get_active_users(app_id, period, new_only=True,
        platform='Android')
    android_stats_prev = get_active_users(app_id, period, new_only=True,
        prev=True, platform='Android')
    return JSONResponse(request, {
        'stats': _prepare_json(stats, period),
        'stats_prev': _prepare_json(stats_prev, period),
        'android_stats': _prepare_json(android_stats, period),
        'android_stats_prev': _prepare_json(android_stats_prev, period),
        'unit': 'User',
    })


def views(request, app_id=None, period=None):
    app_id = int(app_id)
    period = getattr(PERIODS, period.upper())
    stats = get_views(app_id, period, platform='iOS')
    stats_prev = get_views(app_id, period, prev=True, platform='iOS')
    android_stats = get_views(app_id, period, platform='Android')
    android_stats_prev = get_views(app_id, period, prev=True,
        platform='Android')
    return JSONResponse(request, {
        'stats': _prepare_json(stats, period),
        'stats_prev': _prepare_json(stats_prev, period),
        'android_stats': _prepare_json(android_stats, period),
        'android_stats_prev': _prepare_json(android_stats_prev, period),
        'unit': 'View',
    })


def screen_views(request, screen=None, app_id=None, period=None):
    app_id = int(app_id)
    period = getattr(PERIODS, period.upper())
    stats = get_screen_views(app_id, period, screen, platform='iOS')
    stats_prev = get_screen_views(app_id, period, screen, prev=True,
        platform='iOS')
    android_stats = get_screen_views(app_id, period, screen,
        platform='Android')
    android_stats_prev = get_screen_views(app_id, period, screen, prev=True,
        platform='Android')
    return JSONResponse(request, {
        'stats': _prepare_json(stats, period),
        'stats_prev': _prepare_json(stats_prev, period),
        'android_stats': _prepare_json(android_stats, period),
        'android_stats_prev': _prepare_json(android_stats_prev, period),
        'unit': 'View',
    })


def total_users(request, app_id=None, period=None):
    app_id = int(app_id)
    period = getattr(PERIODS, period.upper())
    stats = get_total_users(app_id, period, platform='iOS')
    stats_prev = get_total_users(app_id, period, prev=True, platform='iOS')
    android_stats = get_total_users(app_id, period, platform='Android')
    android_stats_prev = get_total_users(app_id, period, prev=True,
        platform='Android')
    return JSONResponse(request, {
        'stats': _prepare_json(stats, period),
        'stats_prev': _prepare_json(stats_prev, period),
        'android_stats': _prepare_json(android_stats, period),
        'android_stats_prev': _prepare_json(android_stats_prev, period),
        'unit': 'User',
    })


def quick(request, app_id=None, period=None):
    app_id = int(app_id)
    period = getattr(PERIODS, period.upper())
    total_user_count = get_total_user_count(app_id) or 0
    active_users = get_active_user_count(app_id, period) or 0
    new_users = get_new_user_count(app_id, period) or 0
    views = get_view_count(app_id, period) or 0
    return JSONResponse(request, {
        'total_users': total_user_count,
        'active_users': active_users,
        'new_users': new_users,
        'views': views,
    })
