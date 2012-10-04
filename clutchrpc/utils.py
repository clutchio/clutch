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

import calendar
import datetime
import httplib
import os
import re
import sys
import traceback

from urlparse import urljoin

import pytz
import simplejson


ABSOLUTE_URL_RE = re.compile(r'^https?://', re.I)


def get_now():
    return datetime.datetime.utcnow().replace(tzinfo=pytz.utc)


class Response(object):

    def __init__(self, data, code=200, content_type='application/json'):
        self.data = data
        self.code = code
        self.content_type = content_type

    def respond(self, env, start_response):
        start_response('%s %s' % (self.code, httplib.responses[self.code]),
            [('Content-Type', self.content_type)]
        )
        return [self.data]


class ResponseRedirect(Response):

    def __init__(self, data, code=302, content_type='text/plain'):
        self.data = data
        self.code = code
        self.content_type = content_type

    def respond(self, env, start_response):
        url = self.data

        if not ABSOLUTE_URL_RE.match(url):
            is_secure = os.environ.get('HTTPS') == 'on'
            if 'HTTP_X_FORWARDED_HOST' in env:
                host = env['HTTP_X_FORWARDED_HOST']
            elif 'HTTP_HOST' in env:
                host = env['HTTP_HOST']
            else:
                host = env['SERVER_NAME']
                server_port = str(env['SERVER_PORT'])
                if server_port != (is_secure and '443' or '80'):
                    host = '%s:%s' % (host, server_port)
            url = urljoin('%s://%s%s' % (
                'https' if is_secure else 'http',
                host,
                env['PATH_INFO'],
            ), url)

        headers = [
            ('Content-Type', self.content_type),
            ('Location', url),
        ]
        start_response('%s %s' % (self.code, httplib.responses[self.code]),
            headers
        )
        return ['Redirecting to ' + url]


def print_exception(f):
    f.write(''.join(traceback.format_exception(*sys.exc_info())) + '\n\n')


def exception_printer(sender, **kwargs):
    print_exception(sys.stderr)


def render_json(data, code=200):
    return Response(simplejson.dumps(data), code=code)
    return ['Not Found\r\n']


def jsonrpc_response(request_json, data):
    return render_json({
        'id': request_json.get('id'),
        'error': None,
        'result': data,
    })


def jsonrpc_error(request_json, error_code, data=None, code=200):
    if data is None:
        data = {}
    slug = {
        1: 'method-not-specified',
        2: 'method-not-found',
        3: 'unhandled-exception',
        4: 'filename-not-found',
        5: 'archive-not-found',
        6: 'archive-security-exception',
        7: 'app-slug-required',
        8: 'invalid-app-key',
        9: 'invalid-app-slug',
        10: 'invalid-authentication',
        11: 'access-denied',
        12: 'unknown-method',
        13: 'unknown-device',
        14: 'deactivated-app-key',
        15: 'app-over-limit',
    }[error_code]
    detail = {
        1: 'The method %(method)r was not specified.',
        2: 'The method %(method)r was not found',
        3: 'Unhandled exception: %(detail)s',
        4: 'The requested filename was not found: %(filename)s',
        5: 'A valid zip archive was not found in the request',
        6: 'Security flaw found in the archive attempting to be uploaded. It contains a file with path: %(name)s',
        7: 'The X-App-Slug request header must be set to access this functionality',
        8: 'Invalid app key found: %(app_key)s',
        9: 'Invalid app slug found: %(app_slug)s',
        10: 'Your provided authentication is invalid',
        11: 'Your user (%(username)s) does not have access to this app (%(app_slug)s)',
        12: 'Unknown method (%(method)s) was specified',
        13: 'Unkown device (%(device_id)s) was specified',
        14: 'The app key that was specified was deactivated: %(app_key)s',
        15: 'The requested app is over its monthly limit',
    }[error_code] % data
    return render_json({
        'id': request_json.get('id'),
        'error': {
            'code': error_code,
            'slug': slug,
            'detail': detail,
        },
        'result': None,
    }, code=code)


def redirect(url):
    return ResponseRedirect(url)


def datetime_to_timestamp(dt):
    return calendar.timegm(dt.timetuple()) + (dt.microsecond / 1000000.0)
