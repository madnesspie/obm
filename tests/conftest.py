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

# pylint: disable = redefined-outer-name
import dotenv
import pytest

from obm import connectors

# TODO: Check node balance before integration tests
# TODO: Check testnet statuses before testing

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
    is_integration_session = item.config.getoption("--integration")
    is_integration_test = bool(list(item.iter_markers(name="integration")))
    if not is_integration_session and is_integration_test:
        pytest.skip("skipped integration test")


def pytest_configure(config):  # pylint: disable=unused-argument
    """Pytest hook that called before test session.

    Docs:
        https://docs.pytest.org/en/latest/reference.html#_pytest.hookspec.pytest_configure

    Args:
        config: Pytest config object.
    """
    dotenv.load_dotenv(dotenv_path="./.env")


# fixtures


@pytest.fixture
def bitcoin_core():
    return connectors.BitcoinCoreConnector(
        rpc_host="127.0.0.1",
        rpc_port=18332,
        rpc_username="testnet_user",
        rpc_password="testnet_pass",
    )


@pytest.fixture
def geth():
    return connectors.GethConnector(rpc_host="127.0.0.1", rpc_port=8545,)
