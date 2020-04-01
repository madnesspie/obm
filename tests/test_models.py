from obm import models


class TestNode:
    @staticmethod
    def test_init_connector_during_init():
        node = models.Node(
            name='bitcoin-core',
            rpc_host="127.0.0.1",
            rpc_port=18332,
            rpc_username="testnet_user",
            rpc_password="testnet_pass",
        )
        assert node.connector.node == 'bitcoin-core'
        assert node.connector.node == node.name
        assert node.connector.currency == 'bitcoin'
        assert node.connector.currency == node.currency.name
