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

import sys
import traceback

from django.core.signals import got_request_exception

from django.template import add_to_builtins

add_to_builtins('django_ext.templatetags.django_ext_tags')


def print_exception(f):
    f.write(''.join(traceback.format_exception(*sys.exc_info())) + '\n\n')


def exception_printer(sender, **kwargs):
    print_exception(sys.stderr)


got_request_exception.connect(exception_printer)
