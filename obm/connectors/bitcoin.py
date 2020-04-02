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

import aiohttp

from obm.connectors import base


class BitcoinCoreConnector(base.Connector):
    node = "bitcoin-core"
    currency = "bitcoin"

    # TODO: Migrate to __slots__
    METHODS = {
        "rpc_list_transactions": "listtransactions",
        "rpc_estimate_smart_fee": "estimatesmartfee",
        "rpc_send_to_address": "sendtoaddress",
        "rpc_get_block_count": "getblockcount",
        "rpc_get_block": "getblock",
        "rpc_get_transaction": "gettransaction",
        "rpc_get_raw_transaction": "getrawtransaction",
    }

    def __init__(
        self,
        rpc_host: str = "localhost",
        rpc_port: int = 18332,
        rpc_username: str = None,
        rpc_password: str = None,
        loop=None,
        session=None,
        timeout: int = None,
    ):
        if rpc_username is not None and rpc_password is not None:
            self.auth = aiohttp.BasicAuth(rpc_username, rpc_password)
        # self.serializer = serializers.BitcoinCoreTransaction()
        self.headers = {
            "content-type": "application/json",
            "cache-control": "no-cache",
        }
        super().__init__(rpc_host, rpc_port, loop, session, timeout)

    async def wrapper(self, *args, method: str = None) -> Union[dict, list]:
        assert method is not None
        response = await self.call(payload={"method": method, "params": args,})
        return await self.validate(response)

    # Unified interface

    @property
    async def latest_block_number(self) -> int:
        return await self.rpc_get_block_count()

    async def list_transactions(self, count=10, **kwargs) -> List[dict]:
        def _format(tx):
            from_addr = tx["address"] if tx["category"] == "send" else None
            to_addr = tx["address"] if tx["category"] == "receive" else None
            if tx["confirmations"] == -1:
                # This mean that tx out of the main chain
                block_number = -1
            else:
                number_from_end = tx["confirmations"] - 1
                block_number = latest_block_number - number_from_end
            return {
                "txid": tx["txid"],
                "from_address": from_addr,
                "to_address": to_addr,
                "amount": Decimal(str(tx["amount"])),
                "fee": Decimal(str(tx.get("fee", 0))),
                "category": tx["category"],
                "block_number": block_number,
                "timestamp": tx["time"],
                "info": tx,
            }

        latest_block_number = await self.latest_block_number
        txs = await self.rpc_list_transactions(
            kwargs.get("label", "*"),
            count,
            kwargs.get("skip", 0),
            kwargs.get("include_watchonly", False),
        )
        return [_format(tx) for tx in txs]
