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

import logging

from osc_lib.command import command

from designateclient import utils
from designateclient.v2.cli import common
from designateclient.v2.utils import get_all


LOG = logging.getLogger(__name__)


def _format_pool(pool):
    pool.pop('links', None)
    attrib = ''
    for attr in pool.get('attributes') or {}:
        attrib += '{}:{}\n'.format(attr, pool['attributes'][attr])
    pool['attributes'] = attrib
    pool['ns_records'] = '\n'.join(
        str(r.get('hostname', r)) for r in (pool.get('ns_records') or []))


class ListPoolsCommand(command.Lister):
    """List Pools"""

    columns = ['id', 'name']

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)

        common.add_all_common_options(parser)

        parser.add_argument('--name', help='The pool name to filter on.',
                            required=False)
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.dns
        common.set_all_common_headers(client, parsed_args)

        criterion = {}
        if parsed_args.name is not None:
            criterion['name'] = parsed_args.name

        data = get_all(client.pools.list, criterion=criterion)

        cols = list(self.columns)

        return cols, (utils.get_item_properties(s, cols) for s in data)


class ShowPoolCommand(command.ShowOne):
    """Show Pool Details"""

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)

        parser.add_argument('pool', help='The pool name or ID.')

        common.add_all_common_options(parser)

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.dns
        common.set_all_common_headers(client, parsed_args)

        data = client.pools.get(parsed_args.pool)
        _format_pool(data)

        return self.dict2columns(data)


class SharePoolCommand(command.ShowOne):
    """Share a Pool"""

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)

        common.add_all_common_options(parser)

        parser.add_argument('pool', help='The pool name or ID to share.')
        parser.add_argument('target_domain_id',
                            help='Target domain ID to share the pool with.')

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.dns
        common.set_all_common_headers(client, parsed_args)

        data = client.pool_share.create(
            parsed_args.pool,
            parsed_args.target_domain_id
        )

        LOG.info('Pool %s was shared', data['id'])

        data.pop('links', None)

        return self.dict2columns(data)


class ListSharedPoolsCommand(command.Lister):
    """List Pool Shares"""

    columns = [
        'id',
        'pool_id',
        'target_domain_id',
    ]

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)

        common.add_all_common_options(parser)

        parser.add_argument('pool',
                            help='The pool name or ID to list shares for.')

        parser.add_argument('--target-domain-id',
                            help='The target domain ID to filter on.',
                            required=False)
        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.dns
        common.set_all_common_headers(client, parsed_args)

        criterion = {}
        if parsed_args.target_domain_id is not None:
            criterion['target_domain_id'] = parsed_args.target_domain_id

        data = get_all(client.pool_share.list, criterion=criterion,
                       args=[parsed_args.pool])

        cols = list(self.columns)

        return cols, (utils.get_item_properties(s, cols) for s in data)


class ShowSharedPoolCommand(command.ShowOne):
    """Show Pool Share Details"""

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)

        parser.add_argument('pool', help='The pool name or ID.')
        parser.add_argument('pool_share_id',
                            help='The pool share ID to show.')

        common.add_all_common_options(parser)

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.dns
        common.set_all_common_headers(client, parsed_args)

        data = client.pool_share.get(parsed_args.pool,
                                     parsed_args.pool_share_id)
        data.pop('links', None)

        return self.dict2columns(data)


class DeleteSharedPoolCommand(command.Command):
    """Delete a Pool Share"""

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)

        parser.add_argument('pool', help='The pool name or ID.')
        parser.add_argument('pool_share_id',
                            help='The pool share ID to delete.')

        common.add_all_common_options(parser)

        return parser

    def take_action(self, parsed_args):
        client = self.app.client_manager.dns
        common.set_all_common_headers(client, parsed_args)

        client.pool_share.delete(parsed_args.pool, parsed_args.pool_share_id)

        LOG.info('Shared Pool %s was deleted', parsed_args.pool_share_id)
