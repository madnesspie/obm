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
import os

import pytest


@pytest.mark.integration
class TestBitcoinCoreConnector:
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
            ("rpc_estimate_smart_fee", [1], dict,),
            (
                "rpc_send_to_address",
                [os.environ["BITCOIN_CORE_IN_WALLET_ADDRESS"], 0.00001],
                str,
            ),
        ),
    )
    async def test_rpc(bitcoin_core, method_name, args, expected_type):
        method = getattr(bitcoin_core, method_name)
        result = await method(*args)
        assert isinstance(result, expected_type)

    @staticmethod
    async def test_list_transactions(bitcoin_core):
        result = await bitcoin_core.list_transactions(count=1)
        assert len(result) == 1
