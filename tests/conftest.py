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

# pylint: disable = redefined-outer-name
import os

import dotenv
import pytest

from obm import connectors, models

# TODO: Check node balance before integration tests
# TODO: Check testnet statuses before testing

dotenv.load_dotenv(dotenv_path="./.env")
pytest_plugins = "aiohttp.pytest_plugin"

# console options


def pytest_addoption(parser):
    parser.addoption(
        "--integration",
        action="store_true",
        default="",
        help="Run integration tests with main test suite.",
    )


# pytest hooks


def pytest_runtest_setup(item):
    """Pytest hook that called before each test.

    Docs:
        https://docs.pytest.org/en/latest/reference.html#_pytest.hookspec.pytest_runtest_setup

    Args:
        item: Pytest item object (conceptually is test).
    """
    markers = [marker.name for marker in item.iter_markers()]
    is_integration_test_session = item.config.getoption("--integration")
    if not is_integration_test_session and "integration" in markers:
        pytest.skip("skipped integration test")


# fixtures


@pytest.fixture
async def bitcoin_core(loop):
    async with connectors.BitcoinCoreConnector(
        rpc_host=os.getenv("BITCOIN_CORE_HOST", "localhost"),
        rpc_port=int(os.getenv("BITCOIN_CORE_PORT", "18332")),
        rpc_username=os.getenv("BITCOIN_CORE_USERNAME", "testnet_user"),
        rpc_password=os.getenv("BITCOIN_CORE_PASSWORD", "testnet_pass"),
        loop=loop,
    ) as connector:
        yield connector


@pytest.fixture
async def geth(loop):
    async with connectors.GethConnector(
        rpc_host=os.getenv("GETH_HOST", "localhost"),
        rpc_port=int(os.getenv("GETH_PORT", "8545")),
        loop=loop
    ) as connector:
        yield connector


@pytest.fixture
async def bitcoin_core_node(loop):
    async with models.Node(
        name="bitcoin-core",
        rpc_host=os.getenv("BITCOIN_CORE_HOST", "localhost"),
        rpc_port=int(os.getenv("BITCOIN_CORE_PORT", "18332")),
        rpc_username=os.getenv("BITCOIN_CORE_USERNAME", "testnet_user"),
        rpc_password=os.getenv("BITCOIN_CORE_PASSWORD", "testnet_pass"),
        loop=loop,
    ) as node:
        yield node


@pytest.fixture
async def geth_node(loop):
    async with models.Node(
        name="geth",
        rpc_host=os.getenv("GETH_HOST", "localhost"),
        rpc_port=int(os.getenv("GETH_PORT", "8545")),
        loop=loop,
    ) as node:
        yield node


@pytest.fixture(params=["bitcoin-core", "geth"])
def node_name(request):
    return request.param


@pytest.fixture
def node(node_name, geth_node, bitcoin_core_node):
    if node_name == "bitcoin-core":
        return bitcoin_core_node
    if node_name == "geth":
        return geth_node
