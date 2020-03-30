# Copyright 2019-2020 Alexander Polishchuk
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import abc
import functools
from typing import List, Union

import aiohttp

from obm.connectors import exceptions


def _catch_network_errors(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except aiohttp.ServerTimeoutError:
            self = args[0]
            raise exceptions.NetworkTimeoutError(
                f"The request to node was longer "
                f"than timeout: {self.timeout}"
            )
        except aiohttp.ClientError as exc:
            raise exceptions.NetworkError(exc)

    return wrapper


class Connector(abc.ABC):

    DEFAULT_TIMEOUT = 3

    def __init__(self, rpc_host, rpc_port, timeout=None):
        # TODO: validate url
        if timeout is not None:
            if not isinstance(timeout, float):
                raise TypeError("Timeout must be a number")
            if timeout <= 0:
                raise ValueError("Timeout must be greater than zero")

        url = f"{rpc_host}:{rpc_port}"
        self.url = url if url.startswith("http") else "http://" + url
        self.timeout = timeout or self.DEFAULT_TIMEOUT

    def __getattribute__(self, item):
        if item != "METHODS" and item in self.METHODS:
            return functools.partial(self.wrapper, method=self.METHODS[item])
        return super().__getattribute__(item)

    @_catch_network_errors
    async def call(self, payload: dict) -> dict:
        # TODO: Add custom session
        async with aiohttp.ClientSession(
            headers=self.headers, auth=self.auth,
        ) as session:
            async with session.post(self.url, json=payload) as response:
                return await response.json()

    @staticmethod
    async def validate(response: dict) -> Union[dict, list]:
        try:
            if error := response.get("error"):
                raise exceptions.NodeError(error)
            return response["result"]
        except KeyError:
            raise exceptions.NodeInvalidResponceError(response)

    @property
    @abc.abstractmethod
    def node(self) -> str:
        ...

    @property
    @abc.abstractmethod
    def currency(self) -> str:
        ...

    @abc.abstractmethod
    async def wrapper(self, *args, method: str = None) -> Union[dict, list]:
        ...

    @abc.abstractmethod
    async def list_transactions(self, **kwargs) -> List[dict]:
        ...
