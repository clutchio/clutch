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
import plistlib

import simplejson

from boto.s3.connection import S3Connection
from boto.s3.key import Key

from django.core.cache import cache

from clutch import settings

from clutchrpc import db
from clutchrpc import utils


def _get_cache(key):
    cache.get(hashlib.sha1(key).hexdigest())


def _set_cache(key, value, timeout=60):
    cache.set(hashlib.sha1(key).hexdigest(), value, timeout)


def _get_file_list(app, app_version):
    if app_version == 0:
        return {}
    resp = _get_cache('file-list-%s-%s' % (app['slug'], app_version))
    if resp:
        return resp
    conn = S3Connection(settings.AWS_ACCESS_KEY, settings.AWS_ACCESS_SECRET)
    bucket = conn.get_bucket(settings.AWS_BUCKET_NAME, validate=False)
    manifest_key = '%s/%s/meta/manifest.json' % (app['slug'], app_version)
    key = Key(bucket, manifest_key)
    resp = simplejson.loads(key.get_contents_as_string())
    _set_cache('file-list-%s-%s' % (app['slug'], app_version), resp, 999999999)
    return resp


def _get_user_conf(app, app_version):
    if app_version == 0:
        return {}
    resp = _get_cache('user-conf-%s-%s' % (app['slug'], app_version))
    if resp:
        return resp
    conn = S3Connection(settings.AWS_ACCESS_KEY, settings.AWS_ACCESS_SECRET)
    bucket = conn.get_bucket(settings.AWS_BUCKET_NAME, validate=False)
    plist_key = '%s/%s/files/clutch.plist' % (app['slug'], app_version)
    key = Key(bucket, plist_key)
    if not key:
        return {}
    resp = plistlib.readPlistFromString(key.get_contents_as_string())
    _set_cache('user-conf-%s-%s' % (app['slug'], app_version), resp, 999999999)
    return resp


def _get_conf(app, app_version, device):
    dev = None
    if device:
        now = utils.get_now()
        date_updated = now - datetime.timedelta(minutes=6)
        dev = db.get_dev_mode(app['id'], device['user_id'], date_updated)

    user_conf = _get_user_conf(app, app_version)

    timestamps = []
    for key, value in user_conf.items():
        if isinstance(value, datetime.datetime):
            user_conf[key] = utils.datetime_to_timestamp(value)
            timestamps.append(key)

    return dict(user_conf, **{
        '_version': app_version,
        '_url': dev.get('url') if dev else 'http://127.0.0.1:41675/',
        '_dev': bool(dev),
        '_toolbar': dev.get('toolbar') if dev else False,
        '_timestamps': timestamps,
    })


def sync(request_json):
    app = db.get_app_from_key(request_json['_app_key'])
    if not app:
        data = {'app_key': request_json['_app_key']}
        return utils.jsonrpc_error(request_json, 8, data)

    app_version = db.get_app_version_for_bundle_version(app['id'],
        request_json['_bundle_version'])

    # If the app is over the limit and they're not a first-time customer, then
    # we return an error instead of the updated file list.
    if request_json['_app_version'] != '-1' and not app['enabled']:
        return utils.jsonrpc_error(request_json, 15, {})

    device = db.get_device_for_udid_and_app(request_json['_udid'], app['id'])

    return utils.jsonrpc_response(request_json, {
        'files': _get_file_list(app, app_version),
        'conf': _get_conf(app, app_version, device),
    })


def get_file(request_json, filename=None):
    app = db.get_app_from_key(request_json['_app_key'])
    if not app:
        data = {'app_key': request_json['_app_key']}
        return utils.jsonrpc_error(request_json, 8, data)

    conn = S3Connection(settings.AWS_ACCESS_KEY, settings.AWS_ACCESS_SECRET)
    bucket = conn.get_bucket(settings.AWS_BUCKET_NAME, validate=False)
    key = Key(bucket, '%s/%s/files/%s' % (
        app['slug'],
        request_json['_app_version'],
        filename,
    ))
    if key is None:
        return utils.jsonrpc_error(request_json, 4, {'filename': filename},
            code=404)
    if request_json['_platform'] == 'Android':
        return utils.jsonrpc_response(request_json,
            {'url': key.generate_url(120)})
    else:
        return utils.redirect(key.generate_url(120))


def start_dev(request_json, app_slug=None, url=None, toolbar=None):
    user = db.get_user_from_creds(
        request_json.get('_clutch_username'),
        request_json.get('_clutch_password')
    )
    if not user:
        return utils.jsonrpc_error(request_json, 10)

    app = db.get_app_from_user_and_slug(user['id'], app_slug)
    if not app:
        return utils.jsonrpc_error({}, 9, {'app_slug': app_slug})

    if toolbar is None:
        toolbar = True

    db.create_or_update_dev_mode(app['id'], user['id'], url, toolbar)

    return utils.jsonrpc_response(request_json, {
        'development': 'active',
    })


def stop_dev(request_json, app_slug=None):
    user = db.get_user_from_creds(
        request_json.get('_clutch_username'),
        request_json.get('_clutch_password')
    )
    if not user:
        return utils.jsonrpc_error(request_json, 10)

    app = db.get_app_from_user_and_slug(user['id'], app_slug)
    if not app:
        return utils.jsonrpc_error({}, 9, {'app_slug': app_slug})

    db.delete_dev_modes_for_user_and_app(user['id'], app['id'])

    return utils.jsonrpc_response(request_json, {
        'development': 'inactive',
    })


def authenticate(request_json, username=None, password=None, app_slug=None):
    user = db.get_user_from_creds(username, password)
    user_dct = {
        'user_id': user['id'],
        'username': user['username'],
        'email': user['email'],
    } if user else None

    # Start building up the request
    resp = {'user': user_dct}

    # Validate with an app slug if it's provided
    if app_slug is not None:
        app = db.get_app_from_user_and_slug(
            user['id'] if user else None, app_slug)
        if app:
            resp[app_slug] = True
        else:
            resp[app_slug] = False

    return utils.jsonrpc_response(request_json, resp)


def device_authenticate(request_json, device_id=None, app_key=None):
    app = db.get_app_from_key(app_key)

    if app:
        device = db.get_device_for_udid_and_app(device_id, app['id'])
    else:
        device = None

    data = {}
    if device:
        data['user'] = {
            'user_id': device['user_id'],
            'username': device['username'],
            'email': device['email'],
        }
    if app:
        data['app'] = {
            'app_id': app['id'],
            'slug': app['slug'],
            'name': app['name'],
        }
    return utils.jsonrpc_response(request_json, data)


def stats(request_json, logs):
    db.add_bulk_stats_logs(
        request_json['_udid'],
        request_json['_api_version'],
        request_json['_app_version'],
        request_json['_bundle_version'],
        request_json['_app_key'],
        request_json['_platform'],
        logs
    )
    return utils.jsonrpc_response(request_json, {'status': 'ok'})


def get_methods():
    return {
        'stats': stats,
        'device_authenticate': device_authenticate,
        'authenticate': authenticate,
        'stop_dev': stop_dev,
        'start_dev': start_dev,
        'get_file': get_file,
        'sync': sync,
    }
