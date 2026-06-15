# Copyright 2026 Cloudification GmbH. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
import time
import uuid

from designateclient.tests import v2


class TestPool(v2.APIV2TestCase, v2.CrudMixin):
    RESOURCE = 'pools'

    def new_ref(self, **kwargs):
        ref = super().new_ref(**kwargs)
        ref.setdefault("name", uuid.uuid4().hex)
        return ref

    def test_list_pools(self):
        items = [self.new_ref(), self.new_ref()]
        self.stub_url("GET", parts=[self.RESOURCE], json={"pools": items})

        listed = self.client.pools.list()

        self.assertList(items, listed)

    def test_get_pool(self):
        ref = self.new_ref()
        self.stub_entity("GET", entity=ref, id=ref["id"])

        response = self.client.pools.get(ref["id"])

        self.assertRequestBodyIs(None)
        self.assertEqual(ref, response)


class TestPoolShared(v2.APIV2TestCase, v2.CrudMixin):
    def setUp(self):
        super().setUp()
        self.pool_id = str(uuid.uuid4())
        self.target_domain_id = str(uuid.uuid4())
        self.domain_id = str(uuid.uuid4())
        self.created_at = time.strftime("%c")
        self.updated_at = time.strftime("%c")

    def new_ref(self, **kwargs):
        ref = super().new_ref(**kwargs)
        ref.setdefault("pool_id", self.pool_id)
        ref.setdefault("target_domain_id", self.target_domain_id)
        ref.setdefault("domain_id", self.domain_id)
        ref.setdefault("created_at", self.created_at)
        ref.setdefault("updated_at", self.updated_at)
        return ref

    def test_share_a_pool(self):
        json_body = {"target_domain_id": self.target_domain_id}

        expected = self.new_ref()

        self.stub_entity('POST', parts=['pools', self.pool_id, 'shares'],
                         entity=expected, json=json_body)

        response = self.client.pool_share.create(self.pool_id,
                                                 self.target_domain_id)

        self.assertRequestBodyIs(json=json_body)
        self.assertEqual(expected, response)

    def test_get_pool_share(self):
        expected = self.new_ref()

        parts = ["pools", self.pool_id, "shares"]
        self.stub_entity("GET", parts=parts, entity=expected,
                         id=expected["id"])

        response = self.client.pool_share.get(self.pool_id, expected["id"])

        self.assertRequestBodyIs(None)
        self.assertEqual(expected, response)

    def test_list_pool_shares(self):
        items = [
            self.new_ref(),
            self.new_ref()
        ]

        parts = ["pools", self.pool_id, "shares"]
        self.stub_entity('GET', parts=parts, entity={"shared_pools": items})

        listed = self.client.pool_share.list(
            self.pool_id,
            criterion={"target_domain_id": self.target_domain_id})

        self.assertList(items, listed)
        self.assertQueryStringIs(
            f"target_domain_id={self.target_domain_id}")

    def test_delete_pool_share(self):
        ref = self.new_ref()

        parts = ["pools", self.pool_id, "shares", ref["id"]]
        self.stub_url('DELETE', parts=parts)

        response = self.client.pool_share.delete(self.pool_id, ref["id"])

        self.assertRequestBodyIs(None)
        self.assertEqual('', response)
