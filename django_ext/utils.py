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

from django.conf import settings
from django.template import Context, loader
from django.core.mail import send_mail


def datetime_to_timestamp(dt):
    return calendar.timegm(dt.timetuple()) + (dt.microsecond / 1000000.0)


def get_and_update_or_create(model, unique, update):
    """
    Given a model, a dictionary of lookup arguments, and a dictionary of update
    arguments, this convenience function gets an object and updates it in the
    database if necessary.

    Returns a tuple (object, int) where int is 0 if the object was not updated,
    1 if the object was created, and 2 if the object was updated in the
    database.

    >>> resp = get_and_update_or_create(User, {'username': 'example'}, {'email': 'example@example.com'})
    >>> resp
    (<User: example>, 1)
    >>> resp[0].email
    'example@example.com'
    >>> resp = get_and_update_or_create(User, {'username': 'example'}, {'email': 'example@example.com'})
    >>> resp
    (<User: example>, 0)
    >>> resp[0].email
    'example@example.com'
    >>> resp = get_and_update_or_create(User, {'username': 'example'}, {'email': 'another@example.com'})
    >>> resp
    (<User: example>, 2)
    >>> resp[0].email
    'another@example.com'
    """
    obj, created = model.objects.get_or_create(dict(unique, default=update))

    # If we just created it, then the defaults kicked in and we're good to go
    if created:
        return obj, 1

    # Iterate over all of the fields to update, updating if needed, and keeping
    # track of whether any field ever actually changed
    modified = False
    for name, val in update.iteritems():
        if getattr(obj, name) != val:
            modified = True
            setattr(obj, name, val)

    # If a field did change, update the object in the database and return
    if modified:
        obj.save(force_update=True)
        return obj, 2

    # Otherwise the object in the database is up to date
    return obj, 0


def send_template_mail(slug, context, recipient_list,
    from_email=settings.DEFAULT_FROM_EMAIL):
    """
    Loads a template based on the given slug, renders it as a template with
    the given context, and sends it to the given recipients.
    """
    if isinstance(recipient_list, basestring):
        recipient_list = [recipient_list]
    if not isinstance(context, Context):
        context = Context(context)
    subject_tmpl = loader.get_template('mail/%s/subject.txt' % (slug,))
    body_tmpl = loader.get_template('mail/%s/body.txt' % (slug,))
    subject = subject_tmpl.render(context)
    body = body_tmpl.render(context)
    send_mail(subject, body, from_email, recipient_list)
