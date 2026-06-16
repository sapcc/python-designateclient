# Copyright (c) 2016 Hewlett-Packard Enterprise Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from designateclient.v2.base import V2Controller
from designateclient.v2 import utils as v2_utils


class PoolController(V2Controller):
    def list(self, criterion=None, marker=None, limit=None):
        url = self.build_url('/pools', criterion, marker, limit)
        return self._get(url, response_key='pools')

    def get(self, pool):
        pool_id = v2_utils.resolve_by_name(self.list, pool)
        return self._get(f'/pools/{pool_id}')


class PoolShareController(V2Controller):

    def create(self, pool, target_domain_id):
        pool_id = v2_utils.resolve_by_name(self.client.pools.list, pool)
        data = {'target_domain_id': target_domain_id}
        return self._post(f'/pools/{pool_id}/shares', data=data)

    def list(self, pool, criterion=None, marker=None, limit=None):
        pool_id = v2_utils.resolve_by_name(self.client.pools.list, pool)
        url = self.build_url(f'/pools/{pool_id}/shares',
                             criterion, marker, limit)
        return self._get(url, response_key='shared_pools')

    def get(self, pool, pool_share_id):
        pool_id = v2_utils.resolve_by_name(self.client.pools.list, pool)
        return self._get(f'/pools/{pool_id}/shares/{pool_share_id}')

    def delete(self, pool, pool_share_id):
        pool_id = v2_utils.resolve_by_name(self.client.pools.list, pool)
        return self._delete(f'/pools/{pool_id}/shares/{pool_share_id}')
