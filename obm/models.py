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

from obm import connectors


class Currency:
    def __init__(self, name: str, symbol: str = None):
        self.name = name
        self.symbol = symbol

    @classmethod
    def create_for(cls, connector_name: str):
        return cls(name=connectors.MAPPING[connector_name].currency)


class Node:
    def __init__(
        self,
        name: str,
        rpc_port: int,
        currency: Currency = None,
        rpc_host: str = "127.0.0.1",
        rpc_username: str = None,
        rpc_password: str = None,
        loop=None,
    ):
        self.name = self.validate_name(name)
        self.currency = currency or Currency.create_for(name)
        self.rpc_port = rpc_port
        self.rpc_host = rpc_host
        self.rpc_username = rpc_username
        self.rpc_password = rpc_password
        self.connector = connectors.MAPPING[name](
            rpc_host, rpc_port, rpc_username, rpc_password, loop
        )

    @staticmethod
    def validate_name(name: str) -> str:
        return name

    async def close(self):
        await self.connector.close()

    async def list_transactions(self, count=10):
        return await self.connector.list_transactions(count)

    async def estimate_fee(self):
        pass

    async def send_transaction(self):
        pass

    async def create_address(self):
        pass
