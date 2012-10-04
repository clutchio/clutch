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

import simplejson

from clutchrpc import db
from clutchrpc import utils


def send_ab_logs(request_json, logs, guid):
    db.add_bulk_ab_logs(
        guid.replace('-', ''),
        request_json['_api_version'],
        request_json['_app_version'],
        request_json['_bundle_version'],
        request_json['_app_key'],
        request_json['_platform'],
        logs
    )
    return utils.jsonrpc_response(request_json, {'status': 'ok'})


def get_ab_metadata(request_json, guid):
    app = db.get_app_from_key(request_json['_app_key'])
    if app is None:
        data = {'app_key': request_json['_app_key']}
        return utils.jsonrpc_error(request_json, 8, data)

    experiments = dict(((e['id'], e)
        for e in db.get_experiments_for_app(app['id'])))
    variations = db.get_variations_for_app(app['id'])

    metadata = {}
    for variation in variations:
        experiment = experiments[variation['experiment_id']]
        metadata.setdefault(experiment['slug'], {})
        metadata[experiment['slug']].setdefault('weights', [])
        metadata[experiment['slug']]['weights'].append(variation['weight'])
        if experiment['has_data']:
            metadata[experiment['slug']].setdefault('data', [])
            metadata[experiment['slug']]['data'].append(
                simplejson.loads(variation['data']))

    return utils.jsonrpc_response(request_json, {'metadata': metadata})


def get_methods():
    return {
        'get_ab_metadata': get_ab_metadata,
        'send_ab_logs': send_ab_logs,
    }
