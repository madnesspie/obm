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
from typing import List, Union

import aiohttp

from obm import utils
from obm.connectors import base

__all__ = [
    "GethConnector",
]


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
        "rpc_eth_get_transaction_by_hash": "eth_getTransactionByHash",
    }

    def __init__(
        self,
        rpc_host: str = "localhost",
        rpc_port: int = 18332,
        rpc_username: str = None,  # pylint: disable=unused-argument
        rpc_password: str = None,  # pylint: disable=unused-argument
        loop=None,
        session: aiohttp.ClientSession = None,
        timeout: int = None,
    ):
        self.auth = None
        self.headers = {
            "content-type": "application/json",
        }
        super().__init__(rpc_host, rpc_port, loop, session, timeout)

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

    # Geth specific interface

    @staticmethod
    def calc_ether_fee(gas, gas_price):
        return utils.from_wei(utils.to_int(gas) * utils.to_int(gas_price))

    def format_transaction(self, tx, addresses):
        if tx["from"] in addresses and tx["to"] in addresses:
            category = "oneself"
        elif tx["from"] in addresses:
            category = "send"
        elif tx["to"] in addresses:
            category = "receive"
        else:
            assert False, "Unrecognized category"

        if tx["blockNumber"] is None:
            block_number = None
        else:
            block_number = utils.to_int(tx["blockNumber"])

        return {
            "txid": tx["hash"],
            "from_address": tx["from"],
            "to_address": tx["to"],
            "amount": utils.from_wei(utils.to_int(tx["value"])),
            "fee": self.calc_ether_fee(tx["gas"], tx["gasPrice"]),
            "block_number": block_number,
            "category": category,
            "timestamp": None,
            "info": tx,
        }

    async def fetch_blocks_range(
        self,
        start: int,
        end: int = None,
        bunch_size: int = 1000,
        delay: Union[int, float] = 0.1,
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

        def to_bunches(coros, bunch_size):
            bunch_start = 0
            while bunch_start < len(coros):
                yield coros[bunch_start : bunch_start + bunch_size]
                bunch_start += bunch_size

        # TODO: Add validation

        end = end or await self.latest_block_number + 1
        get_block_coros = [
            self.rpc_eth_get_block_by_number(utils.to_hex(n), True)
            for n in range(start, end)
        ]
        blocks_range = []
        for bunch in to_bunches(get_block_coros, bunch_size):
            blocks_range += await asyncio.gather(*bunch)
            await asyncio.sleep(delay)
        return blocks_range

    async def fetch_recent_blocks_range(
        self,
        length: int,
        bunch_size: int = 1000,
        delay: Union[int, float] = 0.1,
    ):
        latest = await self.latest_block_number
        return await self.fetch_blocks_range(
            latest - length, latest + 1, bunch_size, delay
        )

    # Unified interface

    @property
    async def latest_block_number(self) -> int:
        latest_block = await self.rpc_eth_get_block_by_number("latest", True)
        return utils.to_int(latest_block["number"])

    async def create_address(self, password: str = "") -> str:
        return await self.rpc_personal_new_account(password)

    async def estimate_fee(  # pylint: disable=unused-argument
        self,
        from_address: str = None,
        to_address: str = None,
        amount: str = None,
        fee: Union[dict, Decimal] = None,
        data: str = None,
        conf_target: int = 1,
    ) -> Decimal:
        if not to_address:
            raise TypeError(
                "Missing value for required keyword argument transaction"
            )
        if isinstance(fee, dict):
            gas_price = fee.get("gas_price")
            gas = fee.get("gas")
        elif fee is None:
            gas_price = await self.rpc_eth_gas_price()
            gas = None
        else:
            raise TypeError(f"Fee must be dict or None, not {type(fee)}")

        estimated_gas = await self.rpc_eth_estimate_gas(
            {
                "from": from_address,
                "to": to_address,
                "gas": gas,
                "gasPrice": gas_price,
                "value": utils.to_hex(utils.to_wei(amount)) if amount else None,
                "data": data,
            }
        )
        return self.calc_ether_fee(estimated_gas, gas_price)

    async def send_transaction(
        self,
        amount: Decimal,
        to_address: str,
        from_address: str = None,
        fee: Union[dict, Decimal] = None,
        password: str = "",
    ) -> dict:
        tx_data = {
            "from": from_address,
            "to": to_address,
            "value": utils.to_hex(utils.to_wei(amount)),
        }
        # TODO: Validate
        if isinstance(fee, dict):
            tx_data["gas"], tx_data["gasPrice"] = fee["gas"], fee["gas_price"]
        # TODO Execute in bunch
        addresses = await self.rpc_personal_list_accounts()
        txid = await self.rpc_personal_send_transaction(tx_data, password)
        tx = await self.rpc_eth_get_transaction_by_hash(txid)
        return self.format_transaction(tx, addresses)

    async def list_transactions(self, count: int = 10, **kwargs) -> List[dict]:
        """Lists most recent transactions.

        Args:
            count: The number of transactions to return. Defaults to 10.

        Returns:
            Recent transactions list.
        """

        def find_transactions_in(block, addresses):
            return [
                tx
                for tx in block["transactions"]
                if tx["from"] in addresses or tx["to"] in addresses
            ]

        bunch_size = kwargs.get("bunch_size", 1000)
        latest_block_number = await self.latest_block_number
        addresses = await self.rpc_personal_list_accounts()
        start = latest_block_number - bunch_size - 1
        end = latest_block_number + 1
        txs = []
        while True:
            blocks_range = await self.fetch_blocks_range(start, end, bunch_size)
            for block in blocks_range[::-1]:
                txs += find_transactions_in(block, addresses)
                if len(txs) >= count:
                    return [
                        self.format_transaction(tx, addresses)
                        for tx in txs[:count]
                    ]
            if start == 0:
                return [self.format_transaction(tx, addresses) for tx in txs]
            start -= bunch_size
            end -= bunch_size
            if start < 0:
                start = 0
