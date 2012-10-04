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

from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.template import RequestContext

from django.contrib.auth.models import User

from django.contrib.admin.views.decorators import staff_member_required

from accounts.views import _backend_hackend

from stats.interface import get_top_recent_apps


@staff_member_required
def metrics(request):
    TMPL = """
    SELECT
        date_trunc('day', %(date)s),
        COUNT(1)
    FROM %(table)s
    GROUP BY date_trunc('day', %(date)s)
    ORDER BY date_trunc('day', %(date)s) ASC
    """

    def convert(lst):
        return [(calendar.timegm(i[0].timetuple()), i[1]) for i in lst]

    from django.db import connection

    def execute(sql):
        cursor = connection.cursor()
        cursor.execute(sql)
        return cursor.fetchall()

    users = convert(execute(TMPL % {
        'table': 'auth_user',
        'date': 'date_joined',
    }))
    apps = convert(execute(TMPL % {
        'table': 'dashboard_app',
        'date': 'date_created',
    }))
    ab_signups = convert(execute(TMPL % {
        'table': 'accounts_abtestingregistration',
        'date': 'date_created',
    }))

    top_apps = get_top_recent_apps()

    context = {
        'title': 'Metrics',
        'users': users,
        'apps': apps,
        'top_apps': top_apps,
        'ab_signups': ab_signups,
    }
    return render_to_response('admin/metrics.html', context,
        context_instance=RequestContext(request))


@staff_member_required
def admin_login(request, username):
    user = get_object_or_404(User, username__iexact=username)
    _backend_hackend(request, user)
    return HttpResponseRedirect('/')
