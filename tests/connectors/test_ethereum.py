import pytest


@pytest.mark.integration
class TestGethConnector:

    @staticmethod
    async def test_call(geth):
        response = await geth.call({
            'method': 'personal_newAccount',
            'params': ['superstrong'],
            'jsonrpc': '2.0',
            'id': 1,
        })
        assert isinstance(response, dict)
        assert 'result' in response

    @staticmethod
    async def test_call_via_getattribute(geth):
        response = await geth.rpc_personal_new_account('superstrong')
        assert isinstance(response, str)

    # The common RPC methods tests below:

    @staticmethod
    @pytest.mark.parametrize('method_name, args, expected_type', (
        (
            'rpc_personal_new_account',
            ['superstrong'],
            str,
        ),
        (
            'rpc_eth_gas_price',
            [],
            str,
        ),
        (
            'rpc_eth_estimate_gas',
            [{
                'to': '0xe1082e71f1ced0efb0952edd23595e4f76840128',
            }],
            str,
        ),
    ))
    async def test_rpc(geth, method_name, args, expected_type):
        method = getattr(geth, method_name)
        response = await method(*args)
        assert isinstance(response, expected_type)
