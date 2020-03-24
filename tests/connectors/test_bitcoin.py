import pytest


@pytest.mark.integration
class TestBitcoinCoreConnector:

    @staticmethod
    async def test_call(bitcoin_core):
        response = await bitcoin_core.call({
            'method': 'listtransactions',
            'params': ['*', 1000]
        })
        assert isinstance(response, list)

    @staticmethod
    async def test_call_via_getattribute(bitcoin_core):
        response = await bitcoin_core.listtransactions('*', 1000)
        assert isinstance(response, list)
