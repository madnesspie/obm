import abc
import functools

import aiohttp
import requests

from obm.connectors import exceptions

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

    def __init__(self, timeout=None):
        if timeout is not None:
            if not isinstance(timeout, float):
                raise TypeError('Timeout must be a number')
            if timeout <= 0:
                raise ValueError('Timeout must be greater than zero')

        self.timeout = timeout or self.DEFAULT_TIMEOUT

    @property
    @abc.abstractmethod
    def node(self) -> str:
        ...

    @property
    @abc.abstractmethod
    def currency(self) -> str:
        ...

    async def call(self, payload):
        async with aiohttp.ClientSession(
                headers=self.headers,
                auth=self.auth,
        ) as session:
            async with session.post(self.url, json=payload) as response:
                assert response.status == 200
                return await response.json()
