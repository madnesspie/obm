from typing import List, Union

from obm.connectors import base, exceptions
from obm import utils


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
    async def validate(response: dict) -> Union[dict, list]:
        try:
            if error := response.get("error"):
                raise exceptions.NodeError(error)
            return response["result"]
        except KeyError:
            raise exceptions.NodeInvalidResponceError(response)

    async def get_last_blocks_range(self, length):
        latest_block = await self.rpc_eth_get_block_by_number("latest", True)
        latest_block_number = utils.to_int(latest_block["number"])
        # Because connector has just requested one block
        length -= 1
        last_blocks = [
            await self.rpc_eth_get_block_by_number(utils.to_hex(n), True)
            for n in range(
                latest_block_number - length, latest_block_number
            )
        ]
        last_blocks.append(latest_block)
        return last_blocks

    # fmt: off
    @staticmethod
    def find_transactions_in(block: dict, addresses: List[str]) -> List[dict]:
        return [
            tx for tx in block["transactions"]
            if tx["from"] in addresses or tx["to"] in addresses
        ]

    # Unified interface below

    async def list_transactions(self, **kwargs) -> List[dict]:
        blocks_count = kwargs.get("blocks_count", 10)
        block_range = await self.get_last_blocks_range(length=blocks_count)
        addresses = await self.rpc_personal_list_accounts()
        txs = []
        for block in block_range:
            txs += self.find_transactions_in(block, addresses)
        return txs
