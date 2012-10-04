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

import datetime

from django.db.models import F, Sum, Count
from django.db import connections
from django.utils.timezone import now

from dashboard.models import App

from stats.models import ViewDay
from stats.models import ViewMonth, ViewYear
from stats.models import UniqueDay, UniqueMonth
from stats.models import UniqueAllTime


class Periods(object):
    TODAY = 1
    MONTH = 2
    MONTHS = 3
    ALLTIME = 4

    def get_range(self, period, dt=None):
        if dt is None:
            dt = now()
        if period == self.TODAY:
            start = dt.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + datetime.timedelta(days=1)
            return (start, end - datetime.timedelta(microseconds=1))
        elif period == self.MONTH:
            start = dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end = (start + datetime.timedelta(days=45)).replace(day=1)
            return (start, end - datetime.timedelta(microseconds=1))
        elif period == self.MONTHS:
            start, end = self.get_range(self.MONTH, dt)
            start = (start - datetime.timedelta(days=1)).replace(day=1)
            start = (start - datetime.timedelta(days=1)).replace(day=1)
            return (start, end)
        elif period == self.ALLTIME:
            start = dt.replace(year=2011, month=12, day=1, hour=0, minute=0,
                second=0, microsecond=0)
            end = dt.replace(hour=0, minute=0, second=0, microsecond=0)
            end = end + datetime.timedelta(days=1)
            end = end - datetime.timedelta(microseconds=1)
            return (start, end)
        raise ValueError('Invalid period specified')

    def get_prev_range(self, period, dt=None):
        if period == self.ALLTIME:
            return self.get_range(period, dt=dt)
        start, end = self.get_range(period, dt=dt)
        delta = (end - start) + datetime.timedelta(microseconds=1)
        return (start - delta, start - datetime.timedelta(microseconds=1))


PERIODS = Periods()


def _update(created_tuple):
    obj, created = created_tuple
    if created:
        return
    obj.__class__.objects.filter(id=obj.id).update(views=F('views') + 1)


def _get_conn():
    if 'stats' in connections.databases:
        return connections['stats']
    return connections['default']


def _app_or_app_id(app):
    if isinstance(app, App):
        return app.id
    return app


def _unsparse(period, start, end, dct, pre=None):
    delta = {
        PERIODS.TODAY: datetime.timedelta(hours=1),
        PERIODS.MONTH: datetime.timedelta(days=1),
        PERIODS.MONTHS: datetime.timedelta(days=1),
        PERIODS.ALLTIME: datetime.timedelta(days=1),
    }[period]
    current = start
    while current < end:
        if pre is None:
            dct.setdefault(current, 0)
        else:
            val = dct.get(current)
            if val:
                pre = val
            else:
                dct[current] = pre
        current += delta
    return dct


def get_active_users(app, period, platform=None, new_only=False, prev=False):
    if period == PERIODS.ALLTIME and prev:
        return []
    if prev:
        start, end = PERIODS.get_prev_range(period)
    else:
        start, end = PERIODS.get_range(period)
    SQL = """
    SELECT
        timestamp,
        COUNT(1) AS users
    FROM %s
    WHERE
        app_id = %%s AND
        timestamp >= %%s AND
        timestamp <= %%s
        %s
        %s
    GROUP BY timestamp
    """ % (
        'stats_uniquehour' if period == PERIODS.TODAY else 'stats_uniqueday',
        '' if platform is None else 'AND platform = %s',
        'AND new = TRUE' if new_only else '',
    )
    conn = _get_conn()
    cursor = conn.cursor()
    args = [_app_or_app_id(app), start, end]
    if platform is not None:
        args.append(platform)
    cursor.execute(SQL, args)
    dct = _unsparse(period, start, end, dict(cursor.fetchall()))
    return [dict(timestamp=k, stat=dct[k]) for k in sorted(dct.iterkeys())]


def get_views(app, period, platform=None, prev=False):
    if period == PERIODS.ALLTIME and prev:
        return []
    if prev:
        start, end = PERIODS.get_prev_range(period)
    else:
        start, end = PERIODS.get_range(period)
    SQL = """
    SELECT
        timestamp,
        views
    FROM %s
    WHERE
        app_id = %%s AND
        timestamp >= %%s AND
        timestamp <= %%s
        %s
    """ % (
        'stats_viewhour' if period == PERIODS.TODAY else 'stats_viewday',
        '' if platform is None else 'AND platform = %s',
    )
    conn = _get_conn()
    cursor = conn.cursor()
    args = [_app_or_app_id(app), start, end]
    if platform is not None:
        args.append(platform)
    cursor.execute(SQL, args)
    dct = _unsparse(period, start, end, dict(cursor.fetchall()))
    return [dict(timestamp=k, stat=dct[k]) for k in sorted(dct.iterkeys())]


def get_screen_views(app, period, screen, platform=None, prev=False):
    if period == PERIODS.ALLTIME and prev:
        return []
    if prev:
        start, end = PERIODS.get_prev_range(period)
    else:
        start, end = PERIODS.get_range(period)
    SQL = """
    SELECT
        timestamp,
        views
    FROM %s
    WHERE
        app_id = %%s AND
        slug = %%s AND
        timestamp >= %%s AND
        timestamp <= %%s
        %s
    """ % (
        'stats_viewslughour' if period == PERIODS.TODAY else 'stats_viewslugday',
        '' if platform is None else 'AND platform = %s',
    )
    conn = _get_conn()
    cursor = conn.cursor()
    args = [_app_or_app_id(app), screen, start, end]
    if platform is not None:
        args.append(platform)
    cursor.execute(SQL, args)
    dct = _unsparse(period, start, end, dict(cursor.fetchall()))
    return [dict(timestamp=k, stat=dct[k]) for k in sorted(dct.iterkeys())]


def get_screens(app):
    SQL = """
    SELECT slug FROM stats_viewslugyear WHERE app_id = %s GROUP BY slug, app_id
    """
    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute(SQL, [_app_or_app_id(app)])
    return [r[0] for r in cursor.fetchall()]


def get_total_users(app, period, prev=False, platform=None):
    if period == PERIODS.ALLTIME and prev:
        return []
    if prev:
        start, end = PERIODS.get_prev_range(period)
    else:
        start, end = PERIODS.get_range(period)
    SQL = """
    SELECT * FROM (
        SELECT
            %(period)s,
            SUM(users) OVER (ORDER BY %(period)s) AS users
        FROM (
            SELECT
                date_trunc('%(period)s', S.timestamp) AS %(period)s,
                COUNT(1) AS users
            FROM stats_uniquealltime S
            WHERE S.app_id = %%s %(platform)s
            GROUP BY date_trunc('%(period)s', S.timestamp)
            ORDER BY date_trunc('%(period)s', S.timestamp) ASC
        ) AS subquery
    ) AS %(period)s_gated WHERE %(period)s >= %%s AND %(period)s <= %%s
    """ % {
        'period': 'hour' if period == PERIODS.TODAY else 'day',
        'platform': '' if platform is None else 'AND S.platform = %s'
    }
    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute(SQL,
        [_app_or_app_id(app)] + ([] if platform is None else [platform]) + [start, end])
    kwargs = dict(
        app_id=_app_or_app_id(app),
        timestamp__lt=start
    )
    if platform is not None:
        kwargs['platform'] = platform
    pre = UniqueAllTime.objects.filter(**kwargs).count()
    dct = _unsparse(period, start, end, dict(cursor.fetchall()), pre=pre)
    return [dict(timestamp=k, stat=dct[k]) for k in sorted(dct.iterkeys())]


def get_total_user_count(app):
    return UniqueAllTime.objects.filter(app_id=_app_or_app_id(app)).count()


def get_active_user_count(app, period, platform=None):
    app_id = _app_or_app_id(app)

    start, end = PERIODS.get_range(period)
    model = {
        PERIODS.TODAY: UniqueDay,
        PERIODS.MONTH: UniqueMonth,
        PERIODS.MONTHS: UniqueMonth,
        PERIODS.ALLTIME: UniqueAllTime,
    }[period]
    if model != PERIODS.MONTHS:
        kwargs = dict(
            app_id=app_id,
            timestamp__gte=start,
            timestamp__lte=end,
        )
        if platform is not None:
            kwargs['platform'] = platform
        return model.objects.filter(**kwargs).count()

    # If it's the 3-months one, we have to do deduping using DISTINCT
    MONTHS_SQL = """
    SELECT COALESCE(COUNT(DISTINCT udid), 0)
    FROM stats_uniquemonth
    WHERE app_id = %%s AND timestamp >= %%s AND timestamp <= %%s %s
    """ % ('' if platform is None else 'AND platform = %s',)

    conn = _get_conn()
    cursor = conn.cursor()
    args = [_app_or_app_id(app), start, end]
    if platform is not None:
        args.append(platform)
    cursor.execute(MONTHS_SQL, args)
    return cursor.fetchone()[0]


def get_new_user_count(app, period, platform=None):
    app_id = _app_or_app_id(app)

    start, end = PERIODS.get_range(period)
    model = {
        PERIODS.TODAY: UniqueDay,
        PERIODS.MONTH: UniqueMonth,
        PERIODS.MONTHS: UniqueMonth,
        PERIODS.ALLTIME: UniqueAllTime,
    }[period]
    if period != PERIODS.MONTHS:
        kwargs = dict(
            app_id=app_id,
            timestamp__gte=start,
            timestamp__lte=end
        )
        if platform is not None:
            kwargs['platform'] = platform
        if period != PERIODS.ALLTIME:
            kwargs['new'] = True
        return model.objects.filter(**kwargs).count()

    # If it's the 3-months one, we have to do deduping using DISTINCT
    MONTHS_SQL = """
    SELECT COALESCE(COUNT(DISTINCT udid), 0)
    FROM stats_uniquemonth
    WHERE app_id = %%s AND timestamp >= %%s AND timestamp <= %%s AND new IS TRUE %s
    """ % ('' if platform is None else 'AND platform = %s',)
    conn = _get_conn()
    cursor = conn.cursor()
    args = [_app_or_app_id(app), start, end]
    if platform is not None:
        args.append(platform)
    cursor.execute(MONTHS_SQL, args)
    return cursor.fetchone()[0]


def get_view_count(app, period, platform=None):
    app_id = _app_or_app_id(app)

    start, end = PERIODS.get_range(period)
    model = {
        PERIODS.TODAY: ViewDay,
        PERIODS.MONTH: ViewMonth,
        PERIODS.MONTHS: ViewMonth,
        PERIODS.ALLTIME: ViewYear,
    }[period]

    kwargs = dict(
        app_id=app_id,
        timestamp__gte=start,
        timestamp__lte=end,
    )
    if platform is not None:
        kwargs['platform'] = platform

    return model.objects.filter(**kwargs).aggregate(
        Sum('views')).get('views__sum', 0)


def get_current_monthly_user_count(app, platform=None):
    start, end = PERIODS.get_range(PERIODS.MONTH)
    kwargs = dict(
        app_id=_app_or_app_id(app),
        timestamp__gte=start,
        timestamp__lte=end
    )
    if platform is not None:
        kwargs['platform'] = platform
    return UniqueMonth.objects.filter(**kwargs).count()


def get_current_monthly_user_counts():
    start, end = PERIODS.get_range(PERIODS.MONTH)
    return dict(((um['app_id'], um['num']) for um in UniqueMonth.objects.filter(
        timestamp__gte=start,
        timestamp__lte=end
    ).values('app_id').annotate(num=Count('id')).order_by()))


def get_top_recent_apps(limit=20):
    SQL = """
    SELECT app_id, COALESCE(SUM(views), 0)
    FROM stats_viewmonth
    WHERE timestamp >= %s
    GROUP BY app_id
    ORDER BY SUM(views) DESC
    LIMIT %s
    """
    dt = now()
    start = dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    start = start - datetime.timedelta(days=1)
    start = start.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute(SQL, [start, limit])
    rows = list(((int(r[0]), r[1]) for r in cursor.fetchall()))

    apps = App.objects.filter(id__in=[r[0] for r in rows])
    apps = dict(((int(a.id), a) for a in apps))
    print apps

    resp = []
    for row in rows:
        try:
            app = apps[row[0]]
        except KeyError:
            continue
        app.views = row[1]
        resp.append(app)

    return resp
