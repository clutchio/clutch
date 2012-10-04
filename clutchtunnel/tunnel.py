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

from collections import defaultdict
import httplib
import mimetypes
import os
import posixpath
import shutil
import time
import urlparse
import uuid

from gevent import Timeout
from gevent.event import Event
from gevent.queue import Queue, Empty

from clutch import settings

import simplejson as json

REMOTE_URL = getattr(settings, 'CLUTCH_RPC_URL', 'http://127.0.0.1:8088/')
LAST_SEEN = defaultdict(lambda: time.time())
MAX_UNSEEN_CACHE_TIME = getattr(settings, 'TUNNEL_MAX_UNSEEN_CACHE_TIME', 80)
REQUEST_QUEUES = defaultdict(lambda: Queue())
CONTENT_QUEUES = defaultdict(lambda: Queue())
CACHE_PREFIX = getattr(settings, 'TUNNEL_CACHE_PREFIX', '/tmp/tunnelcache')

DEVICE_APP_KEY_CACHE = {}
MAX_BACKLOG_LENGTH = getattr(settings, 'TUNNEL_MAX_BACKLOG_LENGTH', 10)
POLLERS = defaultdict(lambda: [])
BACKLOG = defaultdict(lambda: [])

TIMEOUT = getattr(settings, 'TUNNEL_TIMEOUT', 25)


def remote_call(command, **kwargs):
    headers = kwargs.get('headers', {})
    headers.update({
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    })
    parsed_url = urlparse.urlparse(REMOTE_URL)
    if parsed_url.scheme == 'http':
        conn_class = httplib.HTTPConnection
    else:
        conn_class = httplib.HTTPSConnection
    conn = conn_class(parsed_url.netloc)
    data = json.dumps({
        'method': command,
        'params': kwargs,
        'id': 1,  # Dummy value, we don't need to correlate
    })
    path = (parsed_url.path + '/rpc/').replace('//', '/')
    conn.request('POST', path, data, headers)
    response = conn.getresponse()
    raw_data = response.read()
    conn.close()
    data = json.loads(raw_data)
    if data.get('error'):
        raise ValueError(data['error'])
    return data['result']


def handle_poll(env, start_response):
    try:
        username = env['HTTP_X_CLUTCH_USERNAME']
        password = env['HTTP_X_CLUTCH_PASSWORD']
        app_slug = env['HTTP_X_CLUTCH_APP_SLUG']
    except KeyError:
        start_response('404 Not Found', [('Content-Type', 'text/plain')])
        return ['Not Found\r\n']

    resp = remote_call('authenticate',
        username=username,
        password=password,
        app_slug=app_slug
    )

    # If the server says it's not good, it's not good, so kill it.
    if not (resp.get('user') and resp.get(app_slug)):
        start_response('401 Not Authorized', [('Content-Type', 'text/plain')])
        return ['Not Authorized\r\n']

    # If we haven't seen the user in over N seconds, delete the cached files
    last_seen = LAST_SEEN[(username, app_slug)]
    if (time.time() - last_seen) > MAX_UNSEEN_CACHE_TIME:
        path = posixpath.normpath(
            os.path.join(CACHE_PREFIX, username, app_slug))
        if path.startswith(CACHE_PREFIX):
            shutil.rmtree(path, ignore_errors=True)
    LAST_SEEN[(username, app_slug)] = time.time()

    queue = REQUEST_QUEUES[(username, app_slug)]

    files = []
    while 1:
        try:
            files.append(queue.get_nowait())
        except Empty:
            break

    if not files:
        try:
            files.append(queue.get(timeout=TIMEOUT))
        except Empty:
            pass

    start_response('200 OK', [('Content-Type', 'application/json')])
    return [json.dumps({'files': files})]


def handle_post(env, start_response):
    try:
        ident = env['PATH_INFO'].split('/')[2]
    except IndexError:
        start_response('404 Not Found', [('Content-Type', 'text/plain')])
        return ['Not Found\r\n']
    try:
        request_body_size = int(env.get('CONTENT_LENGTH', 0))
    except ValueError:
        request_body_size = 0
    request_body = env['wsgi.input'].read(request_body_size)
    CONTENT_QUEUES[ident].put(request_body)
    start_response('200 OK', [('Content-Type', 'application/json')])
    return [json.dumps({'result': 'ok'})]


def handle_view(env, start_response):
    split_path = env['PATH_INFO'].split('/')[2:]
    try:
        username = split_path[0]
        app_slug = split_path[1]
    except IndexError:
        start_response('404 Not Found', [('Content-Type', 'text/plain')])
        return ['Not Found\r\n']
    path = '/'.join(split_path[2:])

    # Calculate a local cache directory path for this file, and validate that
    # it's not doing anything crazy like going up a directory
    cache_path = '/'.join(env['PATH_INFO'].split('/')[2:])
    cache_path = posixpath.normpath(os.path.join(CACHE_PREFIX, cache_path))
    if not cache_path.startswith(CACHE_PREFIX):
        start_response('404 Not Found', [('Content-Type', 'text/plain')])
        return ['Not Found\r\n']

    # Check if they're looking for a directory listing, if so, just do it
    if path == '' or path == '/':
        ident = str(uuid.uuid1())
        REQUEST_QUEUES[(username, app_slug)].put({'dir': path, 'uuid': ident})
        try:
            resp = CONTENT_QUEUES[ident].get(timeout=10)
            del CONTENT_QUEUES[ident]
        except Empty:
            del CONTENT_QUEUES[ident]
            start_response('404 Not Found', [('Content-Type', 'text/plain')])
            return ['Not Found\r\n']
        data = '<ul>'
        for item in json.loads(resp):
            data += ('<li><a href="%(item)s/index.html">' +
                '%(item)s</a></li>') % {'item': item}
        data += '</ul>'
        start_response('200 OK', [('Content-Type', 'text/html')])
        return [data]

    # If we haven't seen the user in over N seconds, delete the cached files
    last_seen = LAST_SEEN[(username, app_slug)]
    if (time.time() - last_seen) > MAX_UNSEEN_CACHE_TIME:
        shutil.rmtree(cache_path, ignore_errors=True)

    def _respond(r):
        if r == 'CLUTCH404DOESNOTEXIST':
            start_response('404 Not Found', [('Content-Type', 'text/plain')])
            return ['Not Found\r\n']
        mimetype = mimetypes.guess_type(path) or 'text/plain'
        start_response('200 OK', [('Content-Type', mimetype)])
        return [r]

    # Now we check to see whether there's a file at that path. If so, use it.
    try:
        stat = os.stat(cache_path)
        if stat:
            with open(cache_path, 'r') as f:
                return _respond(f.read())
    except OSError:
        pass

    ident = str(uuid.uuid1())
    REQUEST_QUEUES[(username, app_slug)].put({'path': path, 'uuid': ident})
    try:
        resp = CONTENT_QUEUES[ident].get(timeout=10)
        del CONTENT_QUEUES[ident]
    except Empty:
        del CONTENT_QUEUES[ident]
        start_response('404 Not Found', [('Content-Type', 'text/plain')])
        return ['Not Found\r\n']

    # Make cache directories, if needed
    try:
        os.makedirs(os.path.dirname(cache_path))
    except OSError:
        pass

    # Write the response out to the cache
    with open(cache_path, 'w') as f:
        f.write(resp)
        f.flush()

    return _respond(resp)


def handle_event(env, start_response):
    split_path = env['PATH_INFO'].split('/')
    username, app_slug = split_path[2], split_path[3]

    try:
        request_body_size = int(env.get('CONTENT_LENGTH', 0))
    except ValueError:
        request_body_size = 0
    request_body = env['wsgi.input'].read(request_body_size)
    data = json.loads(request_body)
    resp = remote_call('authenticate',
        username=username,
        password=data.get('password'),
        app_slug=app_slug
    )
    if not (resp.get('user') and resp.get(app_slug)):
        start_response('401 Not Authorized', [('Content-Type', 'text/plain')])
        return ['Not Authorized\r\n']

    # If the message contains the changed file, invalidate the cache
    message = data.get('message')
    if message:
        changed_file = message.get('changed_file')
        if changed_file:
            path = os.path.join(CACHE_PREFIX, username, app_slug, changed_file)
            path = posixpath.normpath(path)
            if path.startswith(CACHE_PREFIX):
                try:
                    os.unlink(path)
                except OSError:
                    path = posixpath.normpath(
                        os.path.join(CACHE_PREFIX, username, app_slug))
                    if path.startswith(CACHE_PREFIX):
                        shutil.rmtree(path, ignore_errors=True)

    key = (username, app_slug)
    message = {
        'id': str(uuid.uuid1()),
        'message': data.get('message'),
    }

    BACKLOG[key].append(message)
    if len(BACKLOG[key]) > MAX_BACKLOG_LENGTH:
        BACKLOG[key] = BACKLOG[key][-MAX_BACKLOG_LENGTH:]

    pollers = POLLERS[key][:]
    POLLERS[key] = []
    for poller in pollers:
        poller.send(message)

    start_response('200 OK', [('Content-Type', 'text/plain')])
    return ['Got the event\r\n']


def handle_phone_poll(env, start_response):
    split_path = env['PATH_INFO'].split('/')
    device_id, app_key = split_path[2], split_path[3]

    # Given the device_id and app_key, get the username and app_slug, either
    # from the cache or from the server.
    resp = DEVICE_APP_KEY_CACHE.get((device_id, app_key))
    if resp:
        username, app_slug = resp
    else:
        resp = remote_call('device_authenticate',
            device_id=device_id,
            app_key=app_key,
        )
        if not (resp.get('user') and resp.get('app')):
            start_response('401 Not Authorized',
                [('Content-Type', 'text/plain')])
            return ['Not Authorized\r\n']
        username = resp['user']['username']
        app_slug = resp['app']['slug']
        DEVICE_APP_KEY_CACHE[(device_id, app_key)] = (username, app_slug)

    key = (username, app_slug)

    qs = urlparse.parse_qs(env.get('QUERY_STRING', ''))
    try:
        cursor = qs['cursor'][0]
        seen = False
        messages = []
        for message in BACKLOG[key]:
            if seen:
                messages.append(message)
            else:
                if cursor == message['id']:
                    seen = True
        if messages:
            start_response('200 OK', [('Content-Type', 'application/json')])
            return [json.dumps({'messages': messages})]
    except (IndexError, KeyError):
        pass

    event = Event()
    POLLERS[key].append(event)
    message = None
    with Timeout(TIMEOUT, False):
        message = event.wait()

    start_response('200 OK', [('Content-Type', 'application/json')])
    return [json.dumps({'messages': [message] if message else []})]


def app(env, start_response):
    if env['PATH_INFO'] == '/':
        start_response('200 OK', [('Content-Type', 'text/plain')])
        return ['This is the clutch tunnel service!\r\n']
    split_path = env['PATH_INFO'].split('/')[1:]
    try:
        action = split_path[0]
    except IndexError:
        start_response('404 Not Found', [('Content-Type', 'text/plain')])
        return ['Not Found\r\n']
    func = {
        'poll': handle_poll,
        'post': handle_post,
        'view': handle_view,
        'phonepoll': handle_phone_poll,
        'event': handle_event,
    }.get(action)
    if not func:
        start_response('404 Not Found', [('Content-Type', 'text/plain')])
        return ['Not Found\r\n']
    return func(env, start_response)


def serve_forever(listener, host, port):
    from gevent.pywsgi import WSGIServer
    print 'Starting clutchtunnel on %s:%s ...' % (host, port)
    WSGIServer(listener, app).serve_forever()


def main():
    try:
        from gevent.baseserver import _tcp_listener
        dir(_tcp_listener)  # Placate PyFlakes
    except ImportError:
        from gevent.server import _tcp_listener

    for root, dirs, files in os.walk(CACHE_PREFIX):
        for d in dirs:
            shutil.rmtree(os.path.join(root, d), ignore_errors=True)

    port = int(getattr(settings, 'CLUTCH_TUNNEL_PORT', 41675))
    host = getattr(settings, 'CLUTCH_TUNNEL_HOST', '0.0.0.0')

    listener = _tcp_listener((host, port), reuse_addr=1)

    serve_forever(listener, host, port)


if __name__ == '__main__':
    main()
