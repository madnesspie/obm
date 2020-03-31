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

    # fmt: off
    @staticmethod
    def find_transactions_in(block: dict, addresses: List[str]) -> List[dict]:
        return [
            tx for tx in block["transactions"]
            if tx["from"] in addresses or tx["to"] in addresses
        ]

    # Geth-specific interface

    async def get_last_blocks_range(
        self,
        length: int,
        bunch_size: int = 1000,
        delay: Union[int, float] = 1,
    ):
        async def retry(coro):
            try:
                return await coro
            except exceptions.NetworkError as e:
                print(f"RETRY with {e}")
                return await coro

        def to_bunches(coros, bunch_size):
            bunch_start = 0
            while bunch_start < len(coros):
                yield coros[bunch_start : bunch_start + bunch_size]
                bunch_start += bunch_size

        latest_block = await self.rpc_eth_get_block_by_number("latest", True)
        latest_block_number = utils.to_int(latest_block["number"])

        # Because connector has just requested one block
        length -= 1
        get_last_block_coros = [
            retry(self.rpc_eth_get_block_by_number(utils.to_hex(n), True))
            for n in range(latest_block_number - length, latest_block_number)
        ]

        last_blocks = []
        for bunch in to_bunches(get_last_block_coros, bunch_size):
            last_blocks += await asyncio.gather(*bunch, return_exceptions=True)
            await asyncio.sleep(delay)
        last_blocks.append(latest_block)
        return last_blocks

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
