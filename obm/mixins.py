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
from decimal import Decimal
from typing import List, Union

from obm import connectors


class ConnectorMixin:

    def __init__(self, *args, **kwargs):
        self.connector = connectors.MAPPING[self.name](
            self.rpc_host,
            self.rpc_port,
            self.rpc_username,
            self.rpc_password,
            self.loop,
            self.session,
        )
        super().__init__(*args, **kwargs)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()

    async def close(self):
        await self.connector.close()

    async def create_address(self, password: str = "") -> str:
        return await self.connector.create_address(password)

    async def estimate_fee(self, transaction: dict = None) -> Decimal:
        return await self.connector.estimate_fee(transaction)

    async def list_transactions(self, count: int = 10) -> List[dict]:
        return await self.connector.list_transactions(count)

    async def send_transaction(
        self,
        amount: Decimal,
        to_address: str,
        from_address: str = None,
        fee: Union[dict, Decimal] = None,
        password: str = "",
    ) -> dict:
        return await self.connector.send_transaction(
            amount, to_address, from_address, fee, password
        )
