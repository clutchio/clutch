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

from gevent import monkey
monkey.patch_all(dns=False)

import cgi
import contextlib
import hashlib
import importlib
import os
import shutil
import tempfile
import zipfile

from StringIO import StringIO

from boto.s3.connection import S3Connection

import simplejson

from clutch import settings

from clutchrpc import utils
from clutchrpc import db


METHODS = {}
for module in ['ab', 'framework']:
    METHODS.update(
        importlib.import_module('clutchrpc.' + module).get_methods()
    )


def responder(func):
    def _inner(env, start_response):
        resp = func(env, start_response)
        if hasattr(resp, 'respond'):
            return resp.respond(env, start_response)
        return resp
    return _inner


@responder
def handle_rpc(env, start_response):
    try:
        content_length = int(env.get('CONTENT_LENGTH', 0))
    except (ValueError, TypeError):
        content_length = 0
    if content_length:
        raw_data = env['wsgi.input'].read(content_length)
    else:
        raw_data = env['wsgi.input'].read()
    request_json = simplejson.loads(raw_data)
    request_json.update({
        '_app_key': env.get('HTTP_X_APP_KEY'),
        '_udid': env.get('HTTP_X_UDID'),
        '_api_version': env.get('HTTP_X_API_VERSION'),
        '_app_version': env.get('HTTP_X_APP_VERSION'),
        '_bundle_version': env.get('HTTP_X_BUNDLE_VERSION'),
        '_clutch_username': env.get('HTTP_X_CLUTCH_USERNAME'),
        '_clutch_password': env.get('HTTP_X_CLUTCH_PASSWORD'),
        '_platform': env.get('HTTP_X_PLATFORM', 'iOS'),
    })
    method = request_json.get('method')
    if not method:
        return utils.jsonrpc_error(request_json, 1, {'method': method})
    func = METHODS.get(method)
    if func is None:
        return utils.jsonrpc_error(request_json, 12, {'method': method})
    print method, raw_data[:100]
    try:
        return func(request_json, **(request_json.get('params') or {}))
    except Exception, e:
        utils.exception_printer(None)
        return utils.jsonrpc_error(request_json, 3, {'detail': str(e)})


@responder
def handle_upload(env, start_response):
    form = cgi.FieldStorage(fp=env['wsgi.input'], environ=env)

    if 'archive' not in form:
        return utils.jsonrpc_error({}, 4)

    app_slug = env.get('HTTP_X_APP_SLUG')
    if not app_slug:
        return utils.jsonrpc_error({}, 7)

    user = db.get_user_from_creds(
        env.get('HTTP_X_CLUTCH_USERNAME'),
        env.get('HTTP_X_CLUTCH_PASSWORD'),
    )
    if not user:
        return utils.jsonrpc_error({}, 10)

    app = db.get_app_from_user_and_slug(user['id'], app_slug)
    if not app:
        return utils.jsonrpc_error({}, 9, {'app_slug': app_slug})

    app_version = db.get_latest_app_version(app['id'])
    if app_version is None:
        app_version = 1
    else:
        app_version += 1

    tmp = StringIO(form['archive'].file.read())
    extracted = tempfile.mkdtemp()
    zip_context = contextlib.closing(
        zipfile.ZipFile(tmp, 'r', zipfile.ZIP_DEFLATED))
    with zip_context as z:
        namelist = z.namelist()
        for name in namelist:
            if name.startswith('..'):
                return utils.jsonrpc_error({}, 6, {'name': name})
            if name.startswith('/'):
                return utils.jsonrpc_error({}, 6, {'name': name})
        z.extractall(extracted)

    # Get rid of the StringIO for memory savings
    del tmp

    # Now we upload that to S3
    conn = S3Connection(settings.AWS_ACCESS_KEY, settings.AWS_ACCESS_SECRET)
    bucket = conn.get_bucket(settings.AWS_BUCKET_NAME)
    for name in namelist:
        upload_fn = '%s/%s/files/%s' % (app_slug, app_version, name)
        key = bucket.new_key(upload_fn)
        key.set_contents_from_filename(os.path.join(extracted, name))

    # Generate an md5 hash of each file in the upload
    hashes = {}
    for name in namelist:
        with open(os.path.join(extracted, name), 'r') as f:
            hashes[name] = hashlib.md5(f.read()).hexdigest()

    # JSON-encode the md5 hashes and upload them to s3
    manifest = simplejson.dumps(hashes)
    manifest_key = '%s/%s/meta/manifest.json' % (app_slug, app_version)
    key = bucket.new_key(manifest_key)
    key.set_contents_from_string(manifest)

    # Delete the temporary directory
    shutil.rmtree(extracted)

    db.create_app_version(app['id'], app_version)

    return utils.jsonrpc_response({}, {'version': app_version})


@responder
def handle_404(env, start_response):
    start_response('404 Not Found', [('Content-Type', 'text/plain')])
    return ['Not Found\r\n']


def app(env, start_response):
    path = env['PATH_INFO']
    if path == '/rpc/':
        return handle_rpc(env, start_response)
    elif path == '/rpc/upload/':
        return handle_upload(env, start_response)
    return handle_404(env, start_response)


def serve_forever(listener, host, port):
    from gevent.pywsgi import WSGIServer
    print 'Starting clutchrpc on %s:%s ...' % (host, port)
    WSGIServer(listener, app).serve_forever()


def main():
    try:
        from gevent.baseserver import _tcp_listener
        dir(_tcp_listener)  # Placate PyFlakes
    except ImportError:
        from gevent.server import _tcp_listener

    port = int(getattr(settings, 'CLUTCH_RPC_PORT', 8088))
    host = getattr(settings, 'CLUTCH_RPC_HOST', '0.0.0.0')

    listener = _tcp_listener((host, port), reuse_addr=1)

    serve_forever(listener, host, port)


if __name__ == '__main__':
    main()
