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

import uuid

from django.db import transaction

from django_ext.http import JSONResponse

from dashboard.models import Device, AppKey, App, Member, Version
from dashboard.utils import norm_bundle


def device_make_primary(request):
    device = Device.objects.get(id=request.GET['device'])
    # First make all of the other devies primary = False
    Device.objects.filter(user=device.user).update(primary=False)
    # Now make this one primary = True
    Device.objects.filter(id=device.id).update(primary=True)
    return {
        'device': device.id,
    }


def device_delete(request):
    device = Device.objects.get(id=request.GET['device'])
    primary = device.primary
    device.delete()
    if primary:
        new_primary = Device.objects.filter(user=request.user)[0]
        Device.objects.filter(id=new_primary.id).update(primary=True)
    return None


def key_deactivate(request):
    app_key = AppKey.objects.get(id=request.GET['app-key'])
    AppKey.objects.filter(id=app_key.id).update(status=AppKey.INACTIVE)
    return None


def key_reactivate(request):
    app_key = AppKey.objects.get(id=request.GET['app-key'])
    AppKey.objects.filter(id=app_key.id).update(status=AppKey.ACTIVE)
    return None


def key_generate(request):
    app = App.objects.get(id=request.GET['app'])
    app_key = AppKey.objects.create(
        app=app,
        key=str(uuid.uuid4())
    )
    return {
        'app_key': app_key.data(),
    }


def member_remove(request):
    member = Member.objects.get(id=request.GET['member'])
    member.delete()
    return None


def version_bundle_save(request):
    try:
        version = Version.objects.get(id=request.GET['version'])
    except Version.DoesNotExist:
        return {'version': None}

    try:
        version.min_bundle = norm_bundle(request.GET['min_bundle'].strip())
        version.max_bundle = norm_bundle(request.GET['max_bundle'].strip())
        version.save(force_update=True)
    except ValueError:
        return {'version': None}

    return {'version': {
        'id': version.id,
        'min_bundle': version.min_bundle,
        'max_bundle': version.max_bundle,
    }}


def quickstart_add_device(request):
    device, _ = Device.objects.get_or_create(
        user=request.user,
        udid=request.GET['device_udid'],
        defaults={
            'name': 'Device Added During QuickStart',
            'primary': True,
        }
    )
    return {'device_id': device.id}

ACTIONS = {
    'device-make-primary': device_make_primary,
    'device-delete': device_delete,
    'key-deactivate': key_deactivate,
    'key-reactivate': key_reactivate,
    'key-generate': key_generate,
    'member-remove': member_remove,
    'version-bundle-save': version_bundle_save,
    'quickstart-add-device': quickstart_add_device,
    'quickstart-add-device-2': quickstart_add_device,
}


def dispatch(request, action=None):
    func = ACTIONS.get(action)
    if not func:
        return JSONResponse(request, {'error': 'invalid-action'})
    try:
        with transaction.commit_on_success():
            resp = func(request) or {}
    except Exception, e:
        return JSONResponse(request, {'error': str(e)})
    resp['args'] = dict(request.GET)
    return JSONResponse(request, {'success': resp})
