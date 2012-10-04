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
import os
import uuid

import psycopg2
import pytz
import simplejson

from gevent.pool import Pool

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clutch.settings')
from django.contrib.auth.hashers import check_password

from clutchrpc import utils
from clutchrpc.pg2 import db


def get_app_from_key(key):
    SQL = """
    SELECT A.*
    FROM dashboard_app A
    LEFT JOIN dashboard_appkey K ON (K.app_id = A.id)
    WHERE K.key = %s AND K.status = 'active'
    """
    return db.fetchone(SQL, [key])


def get_user_from_creds(username, password):
    SQL = "SELECT U.* FROM auth_user U WHERE UPPER(U.username) = UPPER(%s)"
    user = db.fetchone(SQL, [username])
    if user is None:
        return None
    if not check_password(password, user['password']):
        return None
    return user


def get_user_from_id(user_id):
    SQL = "SELECT U.* FROM auth_user U WHERE U.id = %s"
    return db.fetchone(SQL, [user_id])


def get_app_from_user_and_slug(user_id, slug):
    SQL = """
    SELECT A.*
    FROM dashboard_app A
    WHERE UPPER(A.slug) = UPPER(%s) AND A.id IN (
        SELECT M.app_id FROM dashboard_member M where M.user_id = %s
    )
    """
    return db.fetchone(SQL, [slug, user_id])


def get_latest_app_version(app_id):
    SQL = """
    SELECT V.version
    FROM dashboard_version V
    WHERE V.app_id = %s
    ORDER BY v.version DESC
    LIMIT 1
    """
    resp = db.fetchone(SQL, [app_id])
    if resp is None:
        return None
    return resp['version']


def get_app_version_for_bundle_version(app_id, bundle_version):
    SQL = """
    SELECT V.version
    FROM dashboard_version V
    WHERE
        app_id = %s AND
        (V.max_bundle <= %s OR V.max_bundle = '') AND
        (V.min_bundle >= %s OR V.min_bundle = '')
    ORDER BY V.version DESC
    """

    # Normalize the bundle version
    try:
        split_bundle = bundle_version.split('.')
        if not len(split_bundle) == 3:
            raise ValueError('Bundle is not three points')
        split_bundle = map(int, split_bundle)
        norm = '.'.join([str(i).zfill(5) for i in split_bundle])
    except ValueError:
        norm = ''

    resp = db.fetchone(SQL, [app_id, norm, norm])
    if resp:
        return resp['version']
    return 0


def create_app_version(app_id, app_version):
    SQL = """
    INSERT INTO dashboard_version (app_id, version) VALUES (%s, %s)
    """
    db.execute(SQL, [app_id, app_version])


def get_device_for_udid_and_app(udid, app_id):
    SQL = """
    SELECT
        D.*,
        U.username,
        U.email
    FROM dashboard_device D
    LEFT JOIN auth_user U ON (U.id = D.user_id)
    WHERE D.udid = %s AND D.user_id IN (
        SELECT M.user_id FROM dashboard_member M WHERE M.app_id = %s
    )
    LIMIT 1
    """
    return db.fetchone(SQL, [udid, app_id])


def get_dev_mode(app_id, user_id, date_updated):
    SQL = """
    SELECT D.*
    FROM dashboard_developmentmode D
    WHERE D.app_id = %s AND D.user_id = %s AND D.date_updated > %s
    """
    return db.fetchone(SQL, [app_id, user_id, date_updated])


def delete_dev_modes_for_user_and_app(user_id, app_id):
    SQL = """
    DELETE
    FROM dashboard_developmentmode D
    WHERE D.user_id = %s AND D.app_id = %s
    """
    db.execute(SQL, [user_id, app_id])


def create_or_update_dev_mode(app_id, user_id, url, toolbar):
    UPDATE_SQL = """
    UPDATE dashboard_developmentmode
    SET url = %s, toolbar = %s, date_updated = %s
    WHERE app_id = %s AND user_id = %s
    """

    INSERT_SQL = """
    INSERT INTO dashboard_developmentmode
        (app_id, user_id, url, toolbar, date_updated, date_created)
    VALUES (%s, %s, %s, %s, %s, %s)
    """

    now = utils.get_now()
    try:
        db.execute(INSERT_SQL, [app_id, user_id, url, toolbar, now, now])
    except psycopg2.IntegrityError:
        db.execute(UPDATE_SQL, [url, toolbar, now, app_id, user_id])


def get_experiment(app_id, slug):
    SQL = """
    SELECT E.*
    FROM ab_experiment E
    WHERE E.app_id = %s AND UPPER(E.slug) = UPPER(%s)
    """
    return db.fetchone(SQL, [app_id, slug])


def get_experiments_for_app(app_id):
    SQL = """SELECT E.* FROM ab_experiment E WHERE E.app_id = %s"""
    return db.fetchall(SQL, [app_id])


def get_variations_for_app(app_id):
    SQL = """
    SELECT V.*
    FROM ab_variation V
    WHERE V.experiment_id IN (
        SELECT E.id FROM ab_experiment E WHERE E.app_id = %s
    )
    """
    return db.fetchall(SQL, [app_id])


def add_bulk_stats_logs(udid, api_version, app_version, bundle_version,
    app_key, platform, logs):
    """
    Adds bulk stats logs to the database.
    """
    LOG_INSERT_SQL = """
    INSERT INTO stats_log (
        timestamp, action, data, udid, api_version, app_version,
        bundle_version, app_key, uuid, platform
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    UNIQUE_INSERT_SQL = """
    INSERT INTO stats_unique%s (app_id, udid, platform, new, timestamp)
    VALUES (%%s, %%s, %%s, %%s, %%s)
    """

    UNIQUE_ALLTIME_INSERT_SQL = """
    INSERT INTO stats_uniquealltime (app_id, udid, platform)
    VALUES (%s, %s, %s)
    """

    VIEW_UPDATE_SQL = """
    UPDATE stats_view%s
    SET views = views + 1
    WHERE app_id = %%s AND platform = %%s AND timestamp = %%s
    """
    VIEW_INSERT_SQL = """
    INSERT INTO stats_view%s (app_id, platform, timestamp, views)
    VALUES (%%s, %%s, %%s, 1)
    """

    VIEW_SLUG_UPDATE_SQL = """
    UPDATE stats_viewslug%s
    SET views = views + 1
    WHERE app_id = %%s AND platform = %%s AND timestamp = %%s AND slug = %%s
    """
    VIEW_SLUG_INSERT_SQL = """
    INSERT INTO stats_viewslug%s (app_id, platform, timestamp, views, slug)
    VALUES (%%s, %%s, %%s, 1, %%s)
    """

    app = get_app_from_key(app_key)
    if not app:
        return
    app_id = app['id']

    pool = Pool(10)

    def _coro0(log):
        try:
            db.execute(LOG_INSERT_SQL, [
                log['ts'],
                log['action'],
                simplejson.dumps(log['data']),
                udid,
                api_version,
                app_version,
                bundle_version,
                app_key,
                log['uuid'],
                platform,
            ])
        except psycopg2.IntegrityError:
            return

        # Don't care about disappearing in aggregate yet
        if log['action'] == 'viewDidDisappear':
            return

        slug = log['data']['slug']

        ts = datetime.datetime.utcfromtimestamp(log['ts']).replace(
            tzinfo=pytz.utc)
        hour = ts.replace(minute=0, second=0, microsecond=0)
        day = hour.replace(hour=0)
        month = day.replace(day=1)
        year = month.replace(month=1)

        try:
            db.execute(UNIQUE_ALLTIME_INSERT_SQL,
                [app_id, udid, platform])
            new = True
        except psycopg2.IntegrityError:
            new = False

        pt = zip(('hour', 'day', 'month', 'year'), (hour, day, month, year))
        for period, timestamp in pt:
            pool.spawn_link_exception(_coro1, period, timestamp, slug, new)
            pool.spawn_link_exception(_coro2, period, timestamp, slug)
            pool.spawn_link_exception(_coro3, period, timestamp, slug)

    def _coro1(period, timestamp, slug, new):
        try:
            db.execute(UNIQUE_INSERT_SQL % (period,),
                [app_id, udid, platform, new, timestamp])
        except psycopg2.IntegrityError:
            pass

    def _coro2(period, timestamp, slug):
        args = [app_id, platform, timestamp]
        try:
            db.execute(VIEW_INSERT_SQL % (period,), args)
        except psycopg2.IntegrityError:
            db.execute(VIEW_UPDATE_SQL % (period,), args)

    def _coro3(period, timestamp, slug):
        args = [app_id, platform, timestamp, slug]
        try:
            db.execute(VIEW_SLUG_INSERT_SQL % (period,), args)
        except psycopg2.IntegrityError:
            db.execute(VIEW_SLUG_UPDATE_SQL % (period,), args)

    for log in logs:
        pool.spawn_link_exception(_coro0, log)

    pool.join()


def add_bulk_ab_logs(udid, api_version, app_version, bundle_version, app_key,
    platform, logs):
    """
    Adds bulk ab testing logs to the database.
    """
    LOG_INSERT_SQL = """
    INSERT INTO ab_log (
        timestamp, action, data, udid, api_version, app_version,
        bundle_version, app_key, uuid, platform
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    UNIQUE_INSERT_SQL = """
    INSERT INTO ab_uniquemonth (uuid, app_id, udid, month, date_created)
    VALUES (%s, %s, %s, %s, %s)
    """

    EXP_INSERT_SQL = """
    INSERT INTO ab_experiment
        (app_id, name, slug, has_data, num_choices, enabled, date_created)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    EXP_UPDATE_SQL = """
    UPDATE ab_experiment SET num_choices = %s WHERE id = %s
    """

    VARIATION_INSERT_SQL = """
    INSERT INTO ab_variation
        (experiment_id, weight, num, name, data, date_created)
    VALUES (%s, %s, %s, %s, %s, %s)
    """

    TRIAL_INSERT_SQL = """
    INSERT INTO ab_trial
        (uuid, udid, app_id, experiment_id, date_created, date_started,
            date_completed, choice, goal_reached)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    TRIAL_UPDATE_SQL = """
    UPDATE ab_trial
    SET date_completed = %s, goal_reached = %s
    WHERE udid = %s AND experiment_id = %s
    """

    app = get_app_from_key(app_key)
    if not app:
        return
    app_id = app['id']

    now = utils.get_now()

    def insert_ab_log(log):
        try:
            data = log['data']
        except KeyError:
            # TODO: Log error somewhere?
            return

        try:
            db.execute(LOG_INSERT_SQL, [
                log['ts'],
                data['action'],
                simplejson.dumps(log['data']),
                udid,
                api_version,
                app_version,
                bundle_version,
                app_key,
                log['uuid'],
                platform,
            ])
        except psycopg2.IntegrityError:
            return

        ts = datetime.datetime.utcfromtimestamp(log['ts']).replace(
            tzinfo=pytz.utc)
        month = ts.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        try:
            db.execute(UNIQUE_INSERT_SQL,
                [str(uuid.uuid1()), app_id, udid, month, now])
        except psycopg2.IntegrityError:
            pass

        # Don't care about disappearing in aggregate yet
        if data['action'] == 'failure':
            return

        experiment = get_experiment(app_id, data['name'])
        if experiment is None:
            if 'has_data' not in data:
                return
            db.execute(EXP_INSERT_SQL, [
                app_id,
                'Experiment for ' + data['name'],
                data['name'],
                data['has_data'],
                0,
                True,
                now,
            ])
            experiment = get_experiment(app_id, data['name'])

        if 'num_choices' in data:
            if data['num_choices'] != experiment['num_choices']:
                # First update the experiment object
                db.execute(EXP_UPDATE_SQL,
                    [data['num_choices'], experiment['id']])

                # Now create any un-created variation objects
                for i in xrange(data['num_choices']):
                    try:
                        name = 'Test ' + ('ABCDEFGHIJKLMNOPQRSTUVWXYZ'[i],)
                        db.execute(VARIATION_INSERT_SQL, [
                            experiment['id'],
                            0.5 / data['num_choices'],
                            i + 1,
                            name,
                            '{\n}' if experiment['has_data'] else '',
                            now,
                        ])
                    except psycopg2.IntegrityError:
                        pass

            # If it's one of the 'num-choices' actions, we've done that
            # already so we can continue on.
            if data['action'] == 'num-choices':
                return

        if data['action'] == 'test':
            try:
                dt = datetime.datetime.utcfromtimestamp(log['ts']).replace(
                    tzinfo=pytz.utc)
                db.execute(TRIAL_INSERT_SQL, [
                    str(uuid.uuid1()),
                    udid,
                    app_id,
                    experiment['id'],
                    now,
                    dt,
                    None,
                    data['choice'],
                    False,
                ])
            except psycopg2.IntegrityError:
                # What is the expected behavior here?  If a trial is
                # already started for this user, then do we discard the old
                # one, or do we start a new one with a new timestamp and
                # choice?  Do we update the started timestamp on the
                # current one?  Not sure.  For now we just continue and do
                # nothing.
                pass

            return

        if data['action'] == 'goal':
            dt = datetime.datetime.utcfromtimestamp(log['ts']).replace(
                tzinfo=pytz.utc)
            db.execute(TRIAL_UPDATE_SQL, [
                dt,
                True,
                udid,
                experiment['id'],
            ])

    for log in logs:
        insert_ab_log(log)
