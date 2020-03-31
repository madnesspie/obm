# Copyright 2019-2020 Alexander Polishchuk
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

import pytest

from obm import utils


@pytest.mark.integration
class TestGethConnector:
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

    @staticmethod
    async def test_fetch_blocks_range(geth):
        latest = await geth.latest_block_number
        blocks_range = await geth.fetch_blocks_range(
            start=latest - 49, end=latest, bunch_size=5, delay=0.1
        )
        numbers = [utils.to_int(block["number"]) for block in blocks_range]
        assert len(blocks_range) == 50
        prev_number = numbers[0]
        for number in numbers[1:]:
            assert number == prev_number + 1
            prev_number = number

    @staticmethod
    async def test_fetch_blocks_range_with_default_end(geth):
        latest = await geth.latest_block_number
        blocks_range = await geth.fetch_blocks_range(
            start=latest - 99, bunch_size=10, delay=0.1
        )
        numbers = [utils.to_int(block["number"]) for block in blocks_range]
        assert len(blocks_range) == 100
        prev_number = numbers[0]
        for number in numbers[1:]:
            assert number == prev_number + 1
            prev_number = number

    @staticmethod
    @pytest.mark.parametrize(
        "method_name, args, expected_type",
        (
            ("rpc_personal_new_account", ["superstrong"], str,),
            ("rpc_eth_gas_price", [], str,),
            ("rpc_eth_get_block_by_number", ["latest", True], dict),
            ("rpc_personal_list_accounts", [], list),
            (
                "rpc_eth_estimate_gas",
                [{"to": os.environ["GETH_IN_WALLET_ADDRESS"],}],
                str,
            ),
            (
                "rpc_personal_send_transaction",
                [
                    {
                        "from": os.environ["GETH_SEND_FROM_ADDRESS"],
                        "to": os.environ["GETH_IN_WALLET_ADDRESS"],
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

    # @staticmethod
    # async def test_list_transaction(geth):
    #     txs = await geth.list_transactions(blocks_count=5000)
    #     assert isinstance(txs, list)
    #     assert len(txs) >= 1
