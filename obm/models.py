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
import asyncio
from decimal import Decimal
from typing import Optional, Union

import aiohttp

from obm import connectors, mixins, validators

__all__ = [
    "Currency",
    "Node",
]


class Currency:
    def __init__(self, name: str):
        if not isinstance(name, str):
            raise TypeError(
                f"Name must be a string, not '{type(name).__name__}'"
            )
        self.name = validators.validate_currency_is_supported(name)

    @classmethod
    def create_for(cls, connector_name: str):
        return cls(name=connectors.MAPPING[connector_name].currency)


class Node(mixins.ConnectorMixin):
    def __init__(
        self,
        name: str,
        currency: Currency = None,
        rpc_host: str = "localhost",
        rpc_port: Optional[int] = None,
        rpc_username: Optional[str] = None,
        rpc_password: Optional[str] = None,
        loop: Optional[asyncio.AbstractEventLoop] = None,
        session: Optional[aiohttp.ClientSession] = None,
        timeout: Union[int, float] = connectors.DEFAULT_TIMEOUT,
    ):
        if not isinstance(name, str):
            raise TypeError(
                f"Name must be a string, not '{type(name).__name__}'"
            )
        self.name = validators.validate_node_is_supported(name)
        self.currency = currency or Currency.create_for(name)
        self.rpc_port = rpc_port
        self.rpc_host = rpc_host
        self.rpc_username = rpc_username
        self.rpc_password = rpc_password
        self.loop = loop
        self.session = session
        self.timeout = timeout
        # This statement is necessary to perform validation
        assert self.connector.node == self.name
        super().__init__()


class Transaction(mixins.TransactionMixin):
    def __init__(
        self,
        node: Node,
        to_address: str,
        amount: Union[float, Decimal],
        from_address: Optional[str] = None,
        block_number: Optional[int] = None,
        txid: Optional[str] = None,
        category: Optional[str] = None,
        timestamp: Optional[int] = None,
        fee: Optional[Union[dict, float, Decimal]] = None,
    ):
        # TODO: Add validation
        self.node = node
        self.to_address = to_address
        self.amount = amount
        self.from_address = from_address
        self.block_number = block_number
        self.txid = txid
        self.category = category
        self.timestamp = timestamp
        self.fee = fee
        super().__init__()
