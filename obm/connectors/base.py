import abc
import functools
from typing import Union

import aiohttp

# from obm.connectors import exceptions

# def catch_errors(func):

#     @functools.wraps(func)
#     def wrapper(*args, **kwargs):
#         try:
#             return func(*args, **kwargs)
#         except requests.exceptions.Timeout:
#             self = args[0]
#             raise exceptions.NetworkTimeoutError(
#                 f'The request to node was longer '
#                 f'than timeout: {self.timeout}')
#         except requests.exceptions.RequestException as exc:
#             raise exceptions.NetworkError(exc)

#     return wrapper


class Connector(abc.ABC):

    DEFAULT_TIMEOUT = 3

    def __init__(self, rpc_host, rpc_port, timeout=None):
        #TODO: validate url
        if timeout is not None:
            if not isinstance(timeout, float):
                raise TypeError('Timeout must be a number')
            if timeout <= 0:
                raise ValueError('Timeout must be greater than zero')

        url = f'{rpc_host}:{rpc_port}'
        self.url = url if url.startswith('http') else 'http://' + url
        self.timeout = timeout or self.DEFAULT_TIMEOUT

    @property
    @abc.abstractmethod
    def node(self) -> str:
        ...

    @property
    @abc.abstractmethod
    def currency(self) -> str:
        ...

    def __getattribute__(self, item):
        if item != 'METHODS' and item in self.METHODS:
            return functools.partial(self.wrapper, method=item)
        return super().__getattribute__(item)

    @staticmethod
    @abc.abstractmethod
    async def validate(response: dict) -> Union[dict, list]:
        ...

    async def call(self, payload):
        async with aiohttp.ClientSession(
                headers=self.headers,
                auth=self.auth,
        ) as session:
            async with session.post(self.url, json=payload) as response:
                assert response.status == 200
                return await response.json()
