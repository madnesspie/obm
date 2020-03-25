import os

import pytest


@pytest.mark.integration
class TestBitcoinCoreConnector:

    @staticmethod
    async def test_call(bitcoin_core):
        response = await bitcoin_core.call({
            'method': 'listtransactions',
            'params': ['*', 1000]
        })
        assert isinstance(response, dict)
        assert 'result' in response

    @staticmethod
    async def test_call_via_getattribute(bitcoin_core):
        response = await bitcoin_core.rpc_list_transactions('*', 1000)
        assert isinstance(response, list)

    @staticmethod
    @pytest.mark.parametrize(
        'method_name, args, expected_type',
        (
            (
                'rpc_list_transactions',
                ['*', 1000],
                list,
            ),
            (
                'rpc_estimate_smart_fee',
                [1],
                dict,
            ),
            (
                'rpc_send_to_address',
                [os.environ['BITCOIN_CORE_IN_WALLET_ADDRESS'], 0.00001],
                str,
            ),
        ),
    )
    async def test_rpc(bitcoin_core, method_name, args, expected_type):
        method = getattr(bitcoin_core, method_name)
        response = await method(*args)
        assert isinstance(response, expected_type)
