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
        response = await geth.rpc_personal_new_account("superstrong")
        assert isinstance(response, str)

    @staticmethod
    @pytest.mark.parametrize(
        "method_name, args, expected_type",
        (
            ("rpc_personal_new_account", ["superstrong"], str,),
            ("rpc_eth_gas_price", [], str,),
            ("rpc_eth_get_block_by_number", ["latest", True], dict),
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
