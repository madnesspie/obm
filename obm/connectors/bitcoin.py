import abc
import functools
import json

import aiohttp

from obm.connectors import base


class BitcoinCoreConnector(base.Connector):
    node = 'bitcoin-core'
    currency = 'bitcoin'

    def __init__(
        self,
        rpc_host,
        rpc_port,
        rpc_username,
        rpc_password,
        timeout=None,
    ):
        super().__init__(timeout)
        url = f"{rpc_host}:{rpc_port}"
        self.url = url if 'http://' in url else 'http://' + url
        self.auth = aiohttp.BasicAuth(rpc_username, rpc_password)
        self.headers = {
            'content-type': 'application/json',
            'cache-control': 'no-cache'
        }

    # def __getattribute__(self, item):
    #     if attr := getattr(self, item) and callable(attr):
    #         return functools.partial(self.wrapper, method=item)
    #     super().__getattribute__(item)

    # async def wrapper(self, *args, method: str = None):
    #     assert method is not None
    #     return await self.call(payload={
    #         'method': method,
    #         'params': args,
    #     })

    async def call(self, payload):
        response = await super().call(payload)
        try:
            if error := response['error']:
                raise exceptions.NodeError(error)
            return response['result']
        except KeyError:
            raise exceptions.NodeInvalidResponceError(response)
