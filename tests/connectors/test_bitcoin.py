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

    @staticmethod
    async def test_estimate_fee_raise_error_when_errors_key_in_result(
        monkeypatch, bitcoin_core
    ):
        error_1 = "Insufficient data or no feerate found"

        async def mock(*_, **__):
            return {"result": {"errors": [error_1]}}

        monkeypatch.setattr(
            connectors.BitcoinCoreConnector, "call", mock,
        )
        with pytest.raises(exceptions.NodeError) as exc_info:
            await bitcoin_core.estimate_fee()
        assert exc_info.value.args[0] == [error_1]

    @staticmethod
    @pytest.mark.parametrize(
        "mocked_data, expected_result",
        (
            (
                {
                    "amount": 0.00015000,
                    "confirmations": 0,
                    "trusted": False,
                    "txid": "5bfe8e66c05bed33432c96b73da22fe6f17cd45f4269d53987cfb774a7e3a0e9",
                    "walletconflicts": [],
                    "time":1592413084,
                    "timereceived":1592413084,
                    "bip125-replaceable":"no",
                    "details": [
                        {
                            "address": "32A5JFirRRoEz7dhsmqHRNWWe36Z9cmRET",
                            "category": "receive",
                            "amount": 0.00015000,
                            "label": "",
                            "vout":0
                        }
                    ],
                    "hex":"02000000012de8a25f30b4d13101a68a9b92fc58d06130207a80dd5e87a44475513638b964090000006a473044022050a180a78dea52b0d620471dbfbda5853dd3dec356997175387ee692a021d37602203cc0b97058d4521201cc5c7bf827cef98f1ce7b35412ce8ae972fc1b446f09290121030c62d097d1c88b1909df6965576f909b6484398846e9dcb87463cb032ab0a331ffffffff02983a00000000000017a914051e0c36f2daf491ea262e04245c3622e1bdf878877ee50200000000001976a9143ea96e3b0a7f901ebde6a481e3e6677d0e38f37288ac00000000"
                },
                {
                    "category": "receive",
                },
            ),
        ),
        ids=["receive"],
    )
    async def test_in_wallet_transaction(
        monkeypatch, bitcoin_core, mocked_data, expected_result,
    ):
        async def mock_call(*_, **__):
            return {"result": mocked_data}

        @property
        async def mock_latest_block_number(_):
            return 100

        monkeypatch.setattr(
            connectors.BitcoinCoreConnector,
            "call",
            mock_call,
        )
        monkeypatch.setattr(
            connectors.BitcoinCoreConnector,
            "latest_block_number",
            mock_latest_block_number,
        )
        result = await bitcoin_core.fetch_in_wallet_transaction(
            txid=mocked_data["txid"],
        )
        assert result["category"] == expected_result["category"]


@pytest.mark.integration
class TestBitcoinCoreConnectorIntegration:
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
    async def test_send_transaction_on_outside_wallet(bitcoin_core):
        fee = await bitcoin_core.send_transaction(
            amount=0.00001,
            to_address=os.environ.get("BITCOIN_CORE_OUT_WALLET_ADDRESS"),
        )
        assert isinstance(fee, dict)

    @staticmethod
    async def test_fetch_recent_transactions(bitcoin_core):
        txs = await bitcoin_core.fetch_recent_transactions(limit=30)
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
