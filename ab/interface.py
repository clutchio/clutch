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
import hashlib
import itertools

from collections import defaultdict

from django.db import connections
from django.core.cache import cache
from django.utils.timezone import now

from django_ext.utils import datetime_to_timestamp

from dashboard.models import App, AppKey

from ab.models import Experiment


def _get_conn():
    if 'stats' in connections.databases:
        return connections['stats']
    return connections['default']


def _get_exp(app_id, slug):
    try:
        exp = Experiment.objects.get(app=app_id, slug=slug)
    except Experiment.DoesNotExist:
        exp = None
    return exp


def _get_app_id(app_key):
    try:
        app_id = AppKey.objects.get(key=app_key).app_id
    except (AppKey.DoesNotExist, AppKey.MultipleObjectsReturned):
        # TODO: Log error somewhere
        return -1
    return app_id


def get_confidence_data(experiment_id):
    SQL = """
    SELECT
        T.choice,
        SUM(CASE WHEN T.goal_reached THEN 1 ELSE 0 END),
        COUNT(1)
    FROM ab_trial T
    WHERE T.experiment_id = %s
    GROUP BY T.choice
    """
    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute(SQL, [experiment_id])
    resp = {-1: [0, 0]}
    for row in cursor.fetchall():
        resp[row[0]] = (row[1], row[2])
    return resp


def _cleanup_series(series, delta):
    resp = dict(series.iteritems())
    all_timestamps = [s.keys() for s in series.values()]
    try:
        current = min(itertools.chain(*all_timestamps))
        end = max(itertools.chain(*all_timestamps))
    except ValueError:
        return resp
    prev = defaultdict(lambda: {'trials': 0, 'successes': 0})
    while current <= end:
        for choice in resp.keys():
            if current in resp[choice]:
                rc = resp[choice]
                pc = prev[choice]
                rc[current] = {
                    'trials': rc[current]['trials'] + pc['trials'],
                    'successes': rc[current]['successes'] + pc['successes'],
                }
                prev[choice] = rc[current].copy()
            else:
                resp[choice][current] = prev[choice]
        current += delta
    return resp


def get_graphs(experiment_id):
    DAYS_SQL = """
    SELECT ((
        SELECT T1.date_started
        FROM ab_trial T1
        WHERE T1.experiment_id = %s
        ORDER BY T1.date_started DESC
        LIMIT 1
    ) -
    (
        SELECT T2.date_started
        FROM ab_trial T2
        WHERE T2.experiment_id = %s
        ORDER BY T2.date_started ASC
        LIMIT 1
    ))
    """

    SQL = """
    SELECT
        T.choice,
        date_trunc('%(period)s', T.date_started),
        COUNT(1),
        SUM(CASE WHEN T.goal_reached THEN 1 else 0 END)
    FROM ab_trial T
    WHERE T.experiment_id = %%s
    GROUP BY T.choice, date_trunc('%(period)s', T.date_started)
    ORDER BY date_trunc('%(period)s', T.date_started)
    """
    conn = _get_conn()
    cursor = conn.cursor()

    cursor.execute(DAYS_SQL, [experiment_id, experiment_id])
    resp = cursor.fetchone()
    if not resp:
        return {}
    if not resp[0]:
        return {}

    if resp[0] >= datetime.timedelta(days=2):
        period, delta = 'day', datetime.timedelta(days=1)
    else:
        period, delta = 'hour', datetime.timedelta(hours=1)

    cursor.execute(SQL % {'period': period}, [experiment_id])
    choice_series = defaultdict(lambda: {})
    for row in cursor.fetchall():
        choice_series[row[0]][row[1]] = {
            'trials': row[2],
            'successes': row[3],
        }
    return _cleanup_series(choice_series, delta)


def _get_monthly_actives(app_id, month):
    SQL = """
    SELECT COUNT(1) FROM ab_uniquemonth U WHERE U.app_id = %s AND U.month = %s
    """
    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute(SQL, [app_id, month])
    return cursor.fetchall()[0][0]


def get_monthly_actives(app, month=None):
    app_id = app.id if isinstance(app, App) else app
    if month is None:
        month = now()
    month = month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    cache_key = hashlib.sha1('monthly-actives-%s-%s' % (
        app_id,
        datetime_to_timestamp(month),
    )).hexdigest()

    resp = cache.get(cache_key)
    if resp is not None:
        return resp
    resp = _get_monthly_actives(app_id, month)
    cache.set(cache_key, resp, 60)
    return resp
