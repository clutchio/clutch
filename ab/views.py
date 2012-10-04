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

import csv
import datetime

from collections import defaultdict

import simplejson

from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.views.decorators.http import require_POST

from django_ext.http import JSONResponse
from django_ext.utils import datetime_to_timestamp

from django.contrib.auth.decorators import login_required

from dashboard.models import App, Member, AppKey

from ab.models import Experiment, Variation
from ab import interface as abdb
from ab.forms import ExperimentForm


def _get_app_apps(request, app_slug):
    apps = App.objects.filter(member__user=request.user).order_by('id')
    app = get_object_or_404(apps, slug__iexact=app_slug)
    try:
        Member.objects.get(user=request.user, app=app)
    except Member.DoesNotExist:
        return TemplateResponse(request, 'forbidden.html')
    return app, apps


@login_required
def experiment_list(request, app_slug=None):
    app, apps = _get_app_apps(request, app_slug)

    experiments = Experiment.objects.filter(app=app)
    context = {
        'app': app,
        'apps': apps,
        'experiments': experiments,
    }
    return TemplateResponse(request, 'ab/experiment_list.html', context)


@login_required
def experiment_detail(request, app_slug=None, experiment_slug=None):
    app, apps = _get_app_apps(request, app_slug)

    exp = get_object_or_404(Experiment, app=app,
        slug__iexact=experiment_slug)

    variations = Variation.objects.filter(experiment=exp).order_by('num')

    context = {
        'app': app,
        'apps': apps,
        'experiment': exp,
        'variations': variations,
        'total_percentage': 0.0 + sum([v.weight for v in variations]),
        'baseline_percentage': 1.0 - sum([v.weight for v in variations]),
    }
    return TemplateResponse(request, 'ab/experiment_detail.html', context)


@login_required
def experiment_stats(request, app_slug=None, experiment_id=None):
    app, apps = _get_app_apps(request, app_slug)

    exp = get_object_or_404(Experiment, id=int(experiment_id))

    confidence = abdb.get_confidence_data(exp.id)
    graph_data = abdb.get_graphs(exp.id)

    graphs = {-1: [{'successes': 0, 'trials': 0}]}
    for variation in Variation.objects.filter(experiment=exp).order_by('num'):
        graphs[variation.num - 1] = [{'successes': 0, 'trials': 0}]
        confidence.setdefault(variation.num - 1, [0, 0])

    # Convert the series into something nicer and convert datetimes to floats
    for choice in sorted(graph_data.keys()):
        graph = []
        for dt in sorted(graph_data[choice].keys()):
            item = graph_data[choice][dt].copy()
            item['timestamp'] = datetime_to_timestamp(dt)
            graph.append(item)
        graphs[choice] = graph

    return JSONResponse(request, {
        'graphs': graphs,
        'confidence': confidence,
    })


@login_required
def experiment_csv(request, app_slug=None, experiment_id=None):
    app, apps = _get_app_apps(request, app_slug)

    exp = get_object_or_404(Experiment, id=int(experiment_id))

    variations = list(Variation.objects.filter(experiment=exp).order_by('num'))

    graph_data = abdb.get_graphs(exp.id)

    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=%s.%s.csv' % (
        exp.slug,
        datetime.date.today()
    )
    writer = csv.writer(response)

    data = defaultdict(lambda: {})
    all_dts = set()
    all_headers = []

    for choice in sorted(graph_data.keys()):
        choice_name = 'Baseline' if choice == -1 else variations[choice].name

        success_col_name = choice_name + ' Successes'
        trial_col_name = choice_name + ' Trials'

        if success_col_name not in all_headers:
            all_headers.extend([success_col_name, trial_col_name])

        for dt in graph_data[choice].keys():
            all_dts.add(dt)
            data[dt].update({
                success_col_name: graph_data[choice][dt]['successes'],
                trial_col_name: graph_data[choice][dt]['trials'],
            })

    writer.writerow(['Date'] + all_headers)

    for dt in sorted(all_dts):
        row = [str(dt)]
        for header in all_headers:
            val = data[dt].get(header)
            row.append(str(val) if val else '0')
        writer.writerow(row)

    return response


@login_required
def experiment_create(request, app_slug=None):
    app, apps = _get_app_apps(request, app_slug)

    form = ExperimentForm(request.POST or None, app=app, user=request.user)
    if form.is_valid():
        exp = form.save()
        next = reverse('ab_experiment_detail', args=[app_slug, exp.slug])
        return HttpResponseRedirect(next)

    context = {
        'app': app,
        'apps': apps,
        'form': form,
    }
    return TemplateResponse(request, 'ab/experiment_create.html', context)


@login_required
def variation_change_name(request, app_slug=None, variation_id=None):
    app, apps = _get_app_apps(request, app_slug)
    variation = get_object_or_404(Variation, id=variation_id)
    if 'name' not in request.REQUEST:
        raise Http404
    variation.name = request.REQUEST['name']
    variation.save()
    return JSONResponse(request, {'status': 'ok'})


@login_required
def variation_remove(request, app_slug=None, variation_id=None):
    app, apps = _get_app_apps(request, app_slug)
    variation = get_object_or_404(Variation, id=variation_id)
    experiment = variation.experiment
    variation.delete()
    vs = Variation.objects.filter(experiment=experiment).order_by('num')
    for i, variation in enumerate(vs):
        if variation.num != i + 1:
            variation.num = i + 1
            variation.save()
    return JSONResponse(request, {'status': 'ok'})


@login_required
def variation_create(request, app_slug=None, experiment_id=None):
    app, apps = _get_app_apps(request, app_slug)
    experiment = get_object_or_404(Experiment, id=experiment_id)

    vs = Variation.objects.filter(experiment=experiment).order_by('num')
    v = Variation.objects.create(
        experiment=experiment,
        weight=0,
        num=vs.count() + 1,
        name='Test ' + ('ABCDEFGHIJKLMNOPQRSTUVWXYZ'[vs.count()])
    )
    return JSONResponse(request, {
        'id': v.id,
        'name': v.name,
        'weight': v.weight,
    })


@login_required
@require_POST
def experiment_save_data(request, app_slug=None, experiment_id=None):
    # TODO: Respond with error stuff instead of doing assertions
    app, apps = _get_app_apps(request, app_slug)
    experiment = get_object_or_404(Experiment, id=experiment_id)
    assert experiment.app_id == app.id
    items = simplejson.loads(request.raw_post_data)

    total_weight = 0.0
    for item in items:
        total_weight += item['weight']
        if experiment.has_data:
            simplejson.loads(item['data'])

    assert total_weight <= 1.0
    for item in items:
        variation = Variation.objects.get(id=item['id'])
        assert variation.experiment_id == experiment.id
        Variation.objects.filter(id=item['id']).update(
            weight=item['weight'],
            data=item['data'],
        )
    return JSONResponse(request, {'status': 'ok'})


@login_required
@require_POST
def experiment_delete(request, app_slug=None, experiment_id=None):
    # TODO: Respond with error stuff instead of doing assertions
    app, apps = _get_app_apps(request, app_slug)
    experiment = get_object_or_404(Experiment, id=experiment_id)
    assert experiment.app_id == app.id
    experiment.delete()
    return JSONResponse(request, {'status': 'ok'})


@login_required
def quickstart(request, app_slug=None):
    app, apps = _get_app_apps(request, app_slug)
    app_key = AppKey.objects.filter(
        app=app, status=AppKey.ACTIVE).order_by('-date_created')[0].key
    return TemplateResponse(request, 'ab/quickstart.html', {
        'apps': apps,
        'app': app,
        'app_key': app_key,
    })
