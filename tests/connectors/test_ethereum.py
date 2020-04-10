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

from obm import connectors, utils


@pytest.mark.integration
class TestIntegrationGethConnector:
    @staticmethod
    def is_ordered(numbers):
        prev_number = numbers[0]
        for number in numbers[1:]:
            if number != prev_number + 1:
                return False
            prev_number = number
        return True

    @staticmethod
    async def test_call(geth):
        response = await geth.call(
            {
                "method": "personal_newAccount",
                "params": ["superstrong"],
                "jsonrpc": "2.0",
                "id": 1,
            }
        )
        assert isinstance(response, dict)
        assert "result" in response

    @staticmethod
    async def test_call_via_getattribute(geth):
        result = await geth.rpc_personal_new_account("superstrong")
        assert isinstance(result, str)

    async def test_fetch_blocks_range(self, geth):
        latest = await geth.latest_block_number
        blocks_range = await geth.fetch_blocks_range(
            start=latest - 50, end=latest, bunch_size=5, delay=0.1
        )
        numbers = [utils.to_int(block["number"]) for block in blocks_range]
        assert latest not in numbers
        assert len(blocks_range) == 50
        assert self.is_ordered(numbers)

    async def test_fetch_blocks_range_with_default_end(self, geth):
        latest = await geth.latest_block_number
        blocks_range = await geth.fetch_blocks_range(
            start=latest - 100, bunch_size=10, delay=0.1
        )
        numbers = [utils.to_int(block["number"]) for block in blocks_range]
        assert latest in numbers
        assert len(blocks_range) == 101
        assert self.is_ordered(numbers)

    async def test_fetch_recent_blocks_range(self, geth):
        latest = await geth.latest_block_number
        blocks_range = await geth.fetch_recent_blocks_range(
            length=100, bunch_size=10, delay=0.1
        )
        numbers = [utils.to_int(block["number"]) for block in blocks_range]
        assert latest in numbers
        assert len(blocks_range) == 101
        assert self.is_ordered(numbers)

    @staticmethod
    @pytest.mark.parametrize(
        "method_name, args, expected_type",
        (
            ("rpc_personal_new_account", [""], str,),
            ("rpc_eth_gas_price", [], str,),
            ("rpc_eth_get_block_by_number", ["latest", True], dict),
            ("rpc_personal_list_accounts", [], list),
            (
                "rpc_eth_estimate_gas",
                [{"to": os.environ.get("GETH_IN_WALLET_ADDRESS"),}],
                str,
            ),
            (
                "rpc_personal_send_transaction",
                [
                    {
                        "from": os.environ.get("GETH_SEND_FROM_ADDRESS"),
                        "to": os.environ.get("GETH_IN_WALLET_ADDRESS"),
                        "value": utils.to_hex(utils.to_wei(0.0000001)),
                    },
                    "abc",
                ],
                str,
            ),
        ),
    )
    async def test_rpc(geth, method_name, args, expected_type):
        method = getattr(geth, method_name)
        response = await method(*args)
        assert isinstance(response, expected_type)

    @staticmethod
    async def test_create_address(geth):
        address = await geth.create_address()
        assert isinstance(address, str)

    @staticmethod
    async def test_estimate_fee(geth):
        fee = await geth.estimate_fee(
            to_address=os.environ.get("GETH_IN_WALLET_ADDRESS")
        )
        assert isinstance(fee, Decimal)

    @staticmethod
    async def test_send_transaction(geth):
        fee = await geth.send_transaction(
            amount=0.0000001,
            from_address=os.environ.get("GETH_SEND_FROM_ADDRESS"),
            to_address=os.environ.get("GETH_IN_WALLET_ADDRESS"),
            password="abc",
        )
        assert isinstance(fee, dict)

    @staticmethod
    async def test_list_transaction(geth):
        txs = await geth.list_transactions(count=5)
        assert isinstance(txs, list)
        assert len(txs) == 5

        # Tests txs order
        prev_block = txs[0]["block_number"]
        for tx in txs:
            assert tx["block_number"] <= prev_block
            prev_block = tx["block_number"]

    @staticmethod
    async def test_list_transaction_analyse_only_before_genesis_block(
        monkeypatch, geth
    ):
        async def mock(*_):
            return 1500

        monkeypatch.setattr(
            connectors.GethConnector, "latest_block_number", property(mock),
        )
        txs = await geth.list_transactions(count=10)
        assert isinstance(txs, list)
        assert len(txs) == 0
