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

# pylint: disable = redefined-outer-name
import os

import pytest

from obm import serializers
from obm.sync import models


@pytest.fixture
def sync_bitcoin_core_node():
    _node = models.Node(
        name="bitcoin-core",
        rpc_host="127.0.0.1",
        rpc_port=18332,
        rpc_username="testnet_user",
        rpc_password="testnet_pass",
    )
    yield _node
    _node.close()


@pytest.fixture
def sync_geth_node():
    _node = models.Node(name="geth", rpc_port=8545)
    yield _node
    _node.close()


@pytest.fixture(params=["bitcoin-core", "geth"])
def sync_node(
    request, sync_geth_node, sync_bitcoin_core_node
):  # pylint: disable=unused-argument
    if request.param == "bitcoin-core":
        return sync_bitcoin_core_node
    if request.param == "geth":
        return sync_geth_node


@pytest.mark.integration
class TestIntegrationNode:
    @staticmethod
    def test_list_transactions(node):
        txs = node.list_transactions()
        assert isinstance(txs, list)
        assert serializers.Transaction().validate(txs, many=True) == {}

    @staticmethod
    def test_create_address(node):
        txs = node.create_address()
        assert isinstance(txs, str)

    @staticmethod
    def test_send_transaction(node):
        tx_data = {
            "bitcoin-core": {
                "amount": 0.00001,
                "to_address": os.environ.get("BITCOIN_CORE_IN_WALLET_ADDRESS"),
            },
            "geth": {
                "amount": 0.0000001,
                "from_address": os.environ.get("GETH_SEND_FROM_ADDRESS"),
                "to_address": os.environ.get("GETH_IN_WALLET_ADDRESS"),
                "password": "abc",
            },
        }
        tx = node.send_transaction(**tx_data[node.name])
        assert isinstance(tx, dict)
        assert serializers.Transaction().validate(tx) == {}
