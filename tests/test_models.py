# Copyright 2020 Alexander Polishchuk
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import pytest

from obm import models, serializers


class TestNode:
    @staticmethod
    def test_init_connector_during_init():
        node = models.Node(
            name="bitcoin-core",
            rpc_host="127.0.0.1",
            rpc_port=18332,
            rpc_username="testnet_user",
            rpc_password="testnet_pass",
        )
        assert node.connector.node == "bitcoin-core"
        assert node.connector.node == node.name
        assert node.connector.currency == "bitcoin"
        assert node.connector.currency == node.currency.name


@pytest.mark.integration
class TestIntegrationNode:
    @staticmethod
    async def test_list_transactions(node):
        txs = await node.list_transactions()
        assert isinstance(txs, list)
        import pprint
        pprint.pp(txs[1])
        assert serializers.Transaction().validate(txs, many=True) == {}
        # TODO: Test transactions ordering by timestamp
