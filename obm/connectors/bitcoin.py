from typing import Union

import aiohttp

from obm.connectors import base, exceptions


class BitcoinCoreConnector(base.Connector):
    node = 'bitcoin-core'
    currency = 'bitcoin'

    # TODO: Migrate to __slots__
    METHODS = {
        'rpc_list_transactions': 'listtransactions',
        'rpc_estimate_smart_fee': 'estimatesmartfee',
        'rpc_send_to_address': 'sendtoaddress',
    }

    def __init__(self,
                 rpc_host: str = 'localhost',
                 rpc_port: int = 18332,
                 rpc_username: str = None,
                 rpc_password: str = None,
                 timeout: int = None):
        super().__init__(rpc_host, rpc_port, timeout)
        if rpc_username is not None and rpc_password is not None:
            self.auth = aiohttp.BasicAuth(rpc_username, rpc_password)
        self.headers = {
            'content-type': 'application/json',
            'cache-control': 'no-cache'
        }

    async def wrapper(self, *args, method: str = None) -> Union[dict, list]:
        assert method is not None
        response = await self.call(payload={
            'method': method,
            'params': args,
        })
        return await self.validate(response)

    @staticmethod
    async def validate(response: dict) -> Union[dict, list]:
        try:
            error = response['error']
            if error:
                raise exceptions.NodeError(error)
            return response['result']
        except KeyError:
            raise exceptions.NodeInvalidResponceError(response)
