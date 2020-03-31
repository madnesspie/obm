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
import asyncio
from typing import List, Union

from obm import utils
from obm.connectors import base, exceptions


class GethConnector(base.Connector):
    node = "geth"
    currency = "ethereum"

    # TODO: Migrate to __slots__
    METHODS = {
        "rpc_personal_new_account": "personal_newAccount",
        "rpc_eth_estimate_gas": "eth_estimateGas",
        "rpc_eth_gas_price": "eth_gasPrice",
        "rpc_personal_send_transaction": "personal_sendTransaction",
        "rpc_personal_unlock_account": "personal_unlockAccount",
        "rpc_eth_get_block_by_number": "eth_getBlockByNumber",
        "rpc_personal_list_accounts": "personal_listAccounts",
    }

    def __init__(self, rpc_host, rpc_port, timeout=None):
        super().__init__(rpc_host, rpc_port, timeout)
        self.auth = None
        self.headers = {
            "content-type": "application/json",
        }

    async def wrapper(self, *args, method: str = None) -> Union[dict, list]:
        assert method is not None
        response = await self.call(
            payload={
                "method": method,
                "params": args,
                "jsonrpc": "2.0",
                "id": 1,
            }
        )
        return await self.validate(response)

    @staticmethod
    def find_transactions_in(block: dict, addresses: List[str]) -> List[dict]:
        return [
            tx
            for tx in block["transactions"]
            if tx["from"] in addresses or tx["to"] in addresses
        ]

    # Geth-specific interface

    @property
    async def latest_block_number(self):
        latest_block = await self.rpc_eth_get_block_by_number("latest", True)
        return utils.to_int(latest_block["number"])

    async def fetch_blocks_range(
        self,
        start: int,
        end: int = None,
        bunch_size: int = 1000,
        delay: Union[int, float] = 1,
    ) -> List[dict]:
        """Fetches blocks range between start and end bounds.

        Args:
            start: Start fetching bound.
            end: End fetching bound (not inclusive). Defaults to
                latest block number.
            bunch_size: Concurrent RPC request number. Defaults to 1000.
            delay: Delay in seconds between concurrent request bunches.
                Defaults to 1.

        Returns:
            List that contains block range.
        """

        async def retry(coro):
            try:
                return await coro
            except exceptions.NetworkError:
                return await coro

        def to_bunches(coros, bunch_size):
            bunch_start = 0
            while bunch_start < len(coros):
                yield coros[bunch_start : bunch_start + bunch_size]
                bunch_start += bunch_size

        # TODO: Add validation

        end = end or await self.latest_block_number + 1
        get_block_coros = [
            retry(self.rpc_eth_get_block_by_number(utils.to_hex(n), True))
            for n in range(start, end)
        ]
        blocks_range = []
        for bunch in to_bunches(get_block_coros, bunch_size):
            blocks_range += await asyncio.gather(*bunch, return_exceptions=True)
            await asyncio.sleep(delay)
        return blocks_range

    async def fetch_recent_blocks_range(
        self, length: int, bunch_size: int = 1000, delay: Union[int, float] = 1,
    ):
        latest = await self.latest_block_number
        return await self.fetch_blocks_range(
            latest - length, latest + 1, bunch_size, delay
        )

    # Unified interface

    async def list_transactions(self, **kwargs) -> List[dict]:
        blocks_count = kwargs.get("blocks_count", 10)
        block_range = await self.get_last_blocks_range(length=blocks_count)
        addresses = await self.rpc_personal_list_accounts()
        txs = []
        for block in block_range:
            txs += self.find_transactions_in(block, addresses)
        return txs

        # count = kwargs.get("count", 10)
        # txs = []
        # while True:
        #     # get blocks range
        #     # txs += new_txs
        #     if len(txs) >= count:
        #         break
        # return txs[count]
