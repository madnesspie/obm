import os
import collections

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

    # fmt: off
    @staticmethod
    async def test_get_last_blocks_range(geth):
        blocks_range = await geth.get_last_blocks_range(length=5)
        numbers = [utils.to_int(block["number"]) for block in blocks_range]
        assert len(blocks_range) == 5
        assert not [
            item for item, count in collections.Counter(numbers).items()
            if count > 1
        ]

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

    @staticmethod
    async def test_list_transaction(geth):
        txs = await geth.list_transactions(blocks_count=500)
        assert isinstance(txs, list)
        assert len(txs) >= 1
