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
import os
from decimal import Decimal

import pytest

from obm import models, serializers


class TestNode:
    @staticmethod
    @pytest.mark.parametrize(
        "kwargs, error, error_msg",
        (
            (
                {"rpc_host": 111},
                TypeError,
                "PRC host must be a string, not int",
            ),
            (
                {"rpc_port": "WRONG_TYPE"},
                TypeError,
                "PRC port must be an integer, not str",
            ),
        ),
        ids=(
            "wrong host type",
            "wrong port type",
        ),
    )
    def test_init_validation(node_name, kwargs, error, error_msg):
        with pytest.raises(error) as exc_info:
            models.Node(name=node_name, **kwargs)
        assert exc_info.value.args[0] == error_msg

    @staticmethod
    async def test_init_connector_during_init():
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
        await node.close()


@pytest.mark.integration
class TestIntegrationNode:
    @staticmethod
    async def test_list_transactions(node):
        txs = await node.list_transactions(count=2)
        assert isinstance(txs, list)
        assert serializers.Transaction().validate(txs, many=True) == {}

    @staticmethod
    async def test_create_address(node):
        txs = await node.create_address()
        assert isinstance(txs, str)

    @staticmethod
    async def test_estimate_fee(node):
        fee = await node.estimate_fee(
            from_address=os.environ.get("GETH_SEND_FROM_ADDRESS"),
            to_address=os.environ.get("GETH_IN_WALLET_ADDRESS"),
            amount=10,
            data=None,
            fee={"gas": None, "gas_price": None,},
        )
        assert isinstance(fee, Decimal)

    @staticmethod
    async def test_send_transaction(node):
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
        tx = await node.send_transaction(**tx_data[node.name])
        assert isinstance(tx, dict)
        assert tx["fee"] > Decimal("0")
        assert serializers.Transaction().validate(tx) == {}

    @staticmethod
    async def test_send_transaction_subtract_fee_from_amount(node):
        tx_data = {
            "bitcoin-core": {
                "amount": Decimal("0.00001"),
                "to_address": os.environ.get("BITCOIN_CORE_IN_WALLET_ADDRESS"),
                "subtract_fee_from_amount": True,
            },
            "geth": {
                "amount": Decimal("0.00003"),
                "from_address": os.environ.get("GETH_SEND_FROM_ADDRESS"),
                "to_address": os.environ.get("GETH_IN_WALLET_ADDRESS"),
                "subtract_fee_from_amount": True,
                "password": "abc",
            },
        }
        tx = await node.send_transaction(**tx_data[node.name])
        assert isinstance(tx, dict)
        assert tx["fee"] > Decimal("0")
        assert serializers.Transaction().validate(tx) == {}
        assert tx_data[node.name]["amount"] - tx["fee"] == tx["amount"]
