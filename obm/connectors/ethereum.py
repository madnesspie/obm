from typing import Union

from obm.connectors import base, exceptions


class GethConnector(base.Connector):
    node = 'geth'
    currency = 'ethereum'

    # TODO: Migrate to __slots__
    METHODS = ('personal_newAccount',)

    def __init__(self, rpc_host, rpc_port, timeout=None):
        super().__init__(rpc_host, rpc_port, timeout)
        self.auth = None
        self.headers = {
            'content-type': 'application/json',
            'cache-control': 'no-cache'
        }

    async def wrapper(self, *args, method: str = None):
        assert method is not None
        response = await self.call(payload={
            'method': method,
            'params': args,
            'jsonrpc': '2.0',
            'id': 1,
        })
        return await self.validate(response)

    @staticmethod
    async def validate(response: dict) -> Union[dict, list]:
        try:
            error = response.get('error')
            if error:
                raise exceptions.NodeError(error)
            return response['result']
        except KeyError:
            raise exceptions.NodeInvalidResponceError(response)
