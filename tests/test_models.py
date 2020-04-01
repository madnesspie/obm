import pytest

from obm import models, serializers


class TestNode:
    @staticmethod
    def test_init_connector_during_init():
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


@pytest.mark.integration
class TestIntegrationNode:
    @staticmethod
    async def test_list_transactions(node):
        txs = await node.list_transactions()
        assert isinstance(txs, list)
        # import pprint
        # pprint.pp(txs[0])
        assert serializers.Transaction().validate(txs, many=True) == {}
