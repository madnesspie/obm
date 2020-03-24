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
