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

    __connector = None

    @property
    def connector(self):
        if self.__connector:
            return self.__connector
        self.__connector = connectors.MAPPING[self.name](
            self.rpc_host,
            self.rpc_port,
            self.rpc_username,
            self.rpc_password,
            self.loop,
            self.session,
            self.timeout,
        )
        return self.__connector

    async def __aenter__(self):
        await self.open()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()

    async def open(self):
        await self.connector.open()

    async def close(self):
        await self.connector.close()

    async def get_latest_block_number(self):
        return await self.connector.latest_block_number

    async def create_address(self, password: str = "") -> str:
        return await self.connector.create_address(password)

    async def estimate_fee(
        self,
        from_address: str = None,
        to_address: str = None,
        amount: str = None,
        fee: Union[dict, Decimal] = None,
        data: str = None,
        conf_target: int = 1,
    ) -> Decimal:
        return await self.connector.estimate_fee(
            from_address, to_address, amount, fee, data, conf_target,
        )

    async def fetch_recent_transactions(
        self, limit: int = 10, **kwargs,
    ) -> List[dict]:
        return await self.connector.fetch_recent_transactions(limit, **kwargs)

    async def send_transaction(
        self,
        amount: Union[Decimal, float],
        to_address: str,
        from_address: str = None,
        fee: Union[dict, Decimal] = None,
        password: str = "",
        subtract_fee_from_amount: bool = False,
    ) -> dict:
        return await self.connector.send_transaction(
            amount,
            to_address,
            from_address,
            fee,
            password,
            subtract_fee_from_amount,
        )

    async def fetch_in_wallet_transaction(
        self, txid: str
    ) -> dict:
        """Fetches the transaction by txid from a blockchain.

        Args:
            txid: Transaction ID to return.

        Returns:
            Dict that represent the transaction.
        """
        return await self.connector.fetch_in_wallet_transaction(txid)

    async def fetch_in_wallet_transactions(
        self, txids: List[str]
    ) -> List[dict]:
        """Fetches the transactions by txids from a blockchain.

        Args:
            txids: Transaction IDs to return.

        Returns:
            Dict that represent the transactions list.
        """
        return await self.connector.fetch_in_wallet_transactions(txids)


class TransactionMixin:
    async def sync(self):
        """Synchronizes the transaction with blockchain.

        Make sense to synchronize only a transaction that still have
        block_number equals to None. Because a transaction that have already
        added to block is unchanging by blockchain design.

        Returns:
            Synchronized transaction.
        """
        if self.block_number is None:
            tx = await self.node.fetch_in_wallet_transaction(txid=self.txid)
            self.block_number = tx["block_number"]
        return self
