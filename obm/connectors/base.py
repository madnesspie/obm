# Copyright 2020 Alexander Polishchuk
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
import asyncio
import functools
import json
from decimal import Decimal
from typing import List, Optional, Union

import aiohttp

from obm import exceptions

DEFAULT_TIMEOUT = 5 * 60


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


class _DecimalEncoder(json.JSONEncoder):
    def default(self, obj):  # pylint: disable=method-hidden, arguments-differ
        if isinstance(obj, Decimal):
            return str(obj)
        return super().default(obj)


class Connector(abc.ABC):
    def __init__(
        self,
        rpc_host: str,
        rpc_port: int,
        loop: Optional[asyncio.AbstractEventLoop] = None,
        session: Optional[aiohttp.ClientSession] = None,
        timeout: Union[int, float] = DEFAULT_TIMEOUT,
    ):
        if not isinstance(rpc_host, str):
            raise TypeError(
                f"PRC host must be a string, not '{type(rpc_host).__name__}'"
            )
        if not isinstance(rpc_port, int):
            raise TypeError(
                f"PRC port must be an integer, not '{type(rpc_port).__name__}'"
            )
        if session is not None:
            if not isinstance(session, aiohttp.ClientTimeout):
                raise TypeError(
                    f"Session must be a aiohttp.ClientSession, "
                    f"not '{type(session).__name__}'"
                )
        if timeout is not None:
            if not isinstance(timeout, float) and not isinstance(timeout, int):
                raise TypeError(
                    f"Timeout must be a number, not '{type(timeout).__name__}'"
                )
            if timeout <= 0:
                raise ValueError("Timeout must be greater than zero")

        # TODO: Create auth here
        url = f"{rpc_host}:{rpc_port}"
        self.rpc_host = rpc_host
        self.rpc_port = rpc_port
        self.url = url if url.startswith("http") else "http://" + url
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.loop = loop or asyncio.get_event_loop()
        self.session = session

    def __getattribute__(self, item):
        if item != "METHODS" and item in self.METHODS:
            return functools.partial(self.wrapper, method=self.METHODS[item])
        return super().__getattribute__(item)

    async def __aenter__(self):
        await self.open()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()

    async def open(self):
        if self.session is None:
            self.session = aiohttp.ClientSession(
                loop=self.loop,
                headers=self.headers,
                auth=self.auth,
                json_serialize=functools.partial(
                    json.dumps, cls=_DecimalEncoder
                ),
            )

    async def close(self):
        if self.session is not None:
            await self.session.close()
            self.session = None

    @_catch_network_errors
    async def call(self, payload: dict) -> dict:
        await self.open()
        async with self.session.post(  # type: ignore
            url=self.url,
            json=payload,
            timeout=self.timeout,
            raise_for_status=True,
        ) as response:
            return await response.json(
                loads=functools.partial(json.loads, parse_float=Decimal)
            )

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

    # Unified interface

    @property
    @abc.abstractmethod
    async def latest_block_number(self) -> int:
        ...

    @abc.abstractmethod
    async def create_address(self, password: str = "") -> str:
        return await self.rpc_personal_new_account(password)

    @abc.abstractmethod
    async def estimate_fee(
        self,
        from_address: str = None,
        to_address: str = None,
        amount: str = None,
        fee: Union[dict, Decimal] = None,
        data: str = None,
        conf_target: int = 1,
    ) -> Decimal:
        ...

    @abc.abstractmethod
    async def send_transaction(
        self,
        amount: Union[Decimal, float],
        to_address: str,
        from_address: str = None,
        fee: Union[dict, Decimal] = None,
        password: str = "",
        subtract_fee_from_amount: bool = False,
    ) -> dict:
        ...

    @abc.abstractmethod
    async def fetch_recent_transactions(
        self, limit: int = 10, **kwargs,
    ) -> List[dict]:
        """Fetches most recent transactions from a blockchain.

        Args:
            limit: The number of transactions to return. Defaults to 10.

        Returns:
            Most recent transactions list.
        """

    @abc.abstractmethod
    async def fetch_in_wallet_transaction(self, txid: str) -> dict:
        """Fetches the transaction by txid from a blockchain.

        Args:
            txid: Transaction ID to return.

        Returns:
            Dict that represent the transaction.
        """

    async def fetch_in_wallet_transactions(
        self, txids: List[str]
    ) -> List[dict]:
        """Fetches the transactions by txids from a blockchain.

        Args:
            txids: Transaction IDs to return.

        Returns:
            Dict that represent the transactions list.
        """
        batch = [self.fetch_in_wallet_transaction(txid) for txid in txids]
        return await asyncio.gather(*batch)
