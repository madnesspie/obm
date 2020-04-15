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
from collections import defaultdict
from decimal import Decimal
from typing import List, Union

import aiohttp

from obm import exceptions
from obm.connectors import base

__all__ = [
    "BitcoinCoreConnector",
]


class BitcoinCoreConnector(base.Connector):
    node = "bitcoin-core"
    currency = "bitcoin"

    # TODO: Migrate to __slots__
    METHODS = {
        "rpc_list_transactions": "listtransactions",
        "rpc_estimate_smart_fee": "estimatesmartfee",
        "rpc_send_to_address": "sendtoaddress",
        "rpc_get_new_address": "getnewaddress",
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
        session: aiohttp.ClientSession = None,
        timeout: Union[int, float] = None,
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

    # BitcoinCore specific interface

    @staticmethod
    def format_transaction(tx, latest_block_number):
        category = tx.get("category")
        if category is None:
            # Tx is send_transaction output.
            details = {detail["category"]: detail for detail in tx["details"]}
            fee = details["send"]["fee"]
            amount = details["send"]["amount"]
            to_address = details["receive"]["address"]
            from_address = details["send"]["address"]
            category = "send" if from_address != to_address else "oneself"
        else:
            # Tx is list_transactions output.
            if category == "oneself":
                from_address = to_address = tx["address"]
                # Recover original category to prevent lie in info key.
                tx["category"] = "send"
            else:
                to_address = tx["address"]
                from_address = None
            amount = tx["amount"]
            fee = tx.get("fee", 0)

        if tx["confirmations"] == -1:
            # This mean that tx out of the main chain.
            # Reference: https://bitcoin.org/en/developer-reference#listtransactions
            block_number = -1
        elif tx["confirmations"] == 0:
            # Transaction  still in mempool.
            block_number = None
        else:
            number_from_end = tx["confirmations"] - 1
            block_number = latest_block_number - number_from_end

        return {
            "txid": tx["txid"],
            "from_address": from_address,
            "to_address": to_address,
            "amount": abs(amount),
            "fee": abs(fee),
            "block_number": block_number,
            "category": category,
            "timestamp": tx["time"],
            "info": tx,
        }

    # Unified interface

    @property
    async def latest_block_number(self) -> int:
        return await self.rpc_get_block_count()

    async def create_address(  # pylint: disable=unused-argument
        self, password: str = ""
    ) -> str:
        # TODO: Add args
        return await self.rpc_get_new_address()

    async def estimate_fee(  # pylint: disable=unused-argument
        self,
        from_address: str = None,
        to_address: str = None,
        amount: str = None,
        fee: Union[dict, Decimal] = None,
        data: str = None,
        conf_target: int = 1,
    ) -> Decimal:
        result = await self.rpc_estimate_smart_fee(conf_target)
        if errors := result.get("errors"):
            raise exceptions.NodeError(errors)
        return result["feerate"]

    async def send_transaction(  # pylint: disable=unused-argument
        self,
        amount: Union[Decimal, float],
        to_address: str,
        from_address: str = None,
        fee: Union[dict, Decimal] = None,
        password: str = "",
        subtract_fee_from_amount: bool = False,
    ) -> dict:
        # TODO: Validate
        latest_block_number = await self.latest_block_number
        txid = await self.rpc_send_to_address(
            to_address, amount, "", "", subtract_fee_from_amount
        )
        tx = await self.rpc_get_transaction(txid)
        return self.format_transaction(tx, latest_block_number)

    async def list_transactions(self, count: int = 10, **kwargs) -> List[dict]:
        """Lists most recent transactions.

        Args:
            count: The number of transactions to return. Defaults to 10.

        Returns:
            Recent transactions list.
        """

        def combine_duplicates(txs):
            """Combines doubles that is transaction self-sending outcome."""
            txs_by_txid = defaultdict(list)
            for tx in txs:
                txs_by_txid[tx["txid"]].append(tx)
            duplicate_txids = [
                txid
                for txid, tx_or_txs in txs_by_txid.items()
                if len(tx_or_txs) == 2
            ]
            txs = [tx for tx in txs if tx["txid"] not in duplicate_txids]
            for duplicate_txid in duplicate_txids:
                duplicate_txs = {
                    tx["category"]: tx for tx in txs_by_txid[duplicate_txid]
                }
                assert "send" in duplicate_txs and "receive" in duplicate_txs
                duplicate_txs["send"]["category"] = "oneself"
                txs.append(duplicate_txs["send"])
            return txs

        # Double increase the transactions number for feching to prevent cases
        # when transaction was sent on in-wallet address and is present in
        # bitcoin core list tansaction twice with different categories.
        inner_count = count * 2
        latest_block_number = await self.latest_block_number
        txs = await self.rpc_list_transactions(
            kwargs.get("label", "*"),
            inner_count,
            kwargs.get("skip", 0),
            kwargs.get("include_watchonly", False),
        )
        sorted_txs = sorted(
            [
                self.format_transaction(tx, latest_block_number)
                for tx in combine_duplicates(txs)
            ],
            key=lambda x: x["timestamp"],
            reverse=True,
        )
        return sorted_txs[:count]
