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
import os
from decimal import Decimal

import aiohttp
import pytest

from obm import connectors, exceptions


class TestBitcoinCoreConnector:
    @staticmethod
    async def test_estimate_fee_raise_error_when_errors_key_in_result(
        monkeypatch, bitcoin_core
    ):
        error_1 = "Insufficient data or no feerate found"
        monkeypatch.setattr(
            connectors.BitcoinCoreConnector,
            "rpc_estimate_smart_fee",
            lambda *_, **__: {"errors": [error_1]},
        )
        with pytest.raises(exceptions.NetworkError) as exc_info:
            fee = await bitcoin_core.estimate_fee()
        assert exc_info.value.args[0] == [error_1]


class TestBitcoinCoreConnector:
    @staticmethod
    @pytest.mark.parametrize(
        "origin_error, expected_error",
        (
            (aiohttp.ServerTimeoutError, exceptions.NetworkTimeoutError),
            (aiohttp.ClientPayloadError, exceptions.NetworkError),
        ),
        ids=["timeout", "network error",],
    )
    async def test_call_wrap_errors(
        monkeypatch, origin_error, expected_error, bitcoin_core
    ):
        def mock(*_, **__):
            raise origin_error()

        monkeypatch.setattr(aiohttp.ClientSession, "post", mock)

        with pytest.raises(expected_error):
            await bitcoin_core.call(
                payload={"method": "listtransactions", "params": ["*", 1000]}
            )


@pytest.mark.integration
class TestIntegrationBitcoinCoreConnector:
    @staticmethod
    async def test_call(bitcoin_core):
        result = await bitcoin_core.call(
            {"method": "listtransactions", "params": ["*", 1000]}
        )
        assert isinstance(result, dict)
        assert "result" in result

    @staticmethod
    async def test_call_via_getattribute(bitcoin_core):
        response = await bitcoin_core.rpc_list_transactions("*", 1000)
        assert isinstance(response, list)

    @staticmethod
    @pytest.mark.parametrize(
        "method_name, args, expected_type",
        (
            ("rpc_list_transactions", ["*", 1000], list,),
            ("rpc_get_block_count", [], int,),
            ("rpc_estimate_smart_fee", [1], dict,),
            (
                "rpc_send_to_address",
                [os.environ.get("BITCOIN_CORE_IN_WALLET_ADDRESS"), 0.00001],
                # Faucet address
                # ["2NGZrVvZG92qGYqzTLjCAewvPZ7JE8S8VxE", 0.00001],
                str,
            ),
        ),
    )
    async def test_rpc(bitcoin_core, method_name, args, expected_type):
        method = getattr(bitcoin_core, method_name)
        result = await method(*args)
        assert isinstance(result, expected_type)

    # Test unified interface

    @staticmethod
    async def test_create_address(bitcoin_core):
        address = await bitcoin_core.create_address()
        assert isinstance(address, str)

    @staticmethod
    async def test_estimate_fee(bitcoin_core):
        fee = await bitcoin_core.estimate_fee()
        assert isinstance(fee, Decimal)

    @staticmethod
    async def test_send_transaction(bitcoin_core):
        fee = await bitcoin_core.send_transaction(
            amount=0.00001,
            to_address=os.environ.get("BITCOIN_CORE_IN_WALLET_ADDRESS"),
        )
        assert isinstance(fee, dict)

    @staticmethod
    async def test_list_transactions(bitcoin_core):
        txs = await bitcoin_core.list_transactions(count=30)
        assert len(txs) == 30

        # Tests block_number calculation
        block_number_checked = False
        for tx in txs:
            if tx["info"]["confirmations"] <= 0:
                # Tx out of main chain or still in mempool.
                continue
            block_number_checked = True
            block = await bitcoin_core.rpc_get_block(tx["info"]["blockhash"])
            assert block["height"] == tx["block_number"]
        assert block_number_checked

        # Tests txs order
        prev_ts = txs[0]["timestamp"]
        for tx in txs:
            assert tx["timestamp"] <= prev_ts
            prev_ts = tx["timestamp"]
