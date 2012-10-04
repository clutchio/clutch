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


def norm_bundle(s):
    split_bundle = s.split('.')
    if not len(split_bundle) == 3:
        raise ValueError('Bundle is not three points')
    split_bundle = map(int, split_bundle)
    return '.'.join([str(i).zfill(5) for i in split_bundle])
