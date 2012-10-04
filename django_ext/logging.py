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

import socket
import time

import simplejson


def log_event(logger, event, request=None, data=None,
    # Hostname like this for performance hack
    _hostname=socket.gethostname()):
    if request.path.startswith('/admin'):
        return
    if not data:
        data = {}
    data.update({
        'event': event,
        'ts': time.time(),
        'hostname': _hostname,
    })
    has_session = getattr(request, 'session', None)
    if request:
        data.update({
            'uuid': getattr(request, 'uuid', None),
            'trk': getattr(request, 'trk', None),
        })
        if has_session and request.user.is_authenticated():
            data.update({
                'user_id': request.user.id,
                'username': request.user.username,
            })
    logger.info(simplejson.dumps(data))
