# pylint: disable = redefined-outer-name
import pytest

from obm import connectors

# TODO: Check node balance before integration tests

pytest_plugins = 'aiohttp.pytest_plugin'

# console options


def pytest_addoption(parser):
    parser.addoption(
        '--integration',
        action='store_true',
        default='',
        help='Run integration tests with main test suite.',
    )


# pytest hooks


def pytest_runtest_setup(item):
    """Pytest hook that called before each test.

    Docs:
        https://docs.pytest.org/en/latest/reference.html#_pytest.hookspec.pytest_runtest_setup

    Args:
        item: Pytest item object (conceptually is test).
    """
    is_integration_session = item.config.getoption('--integration')
    is_integration_test = bool(list(item.iter_markers(name='integration')))
    if not is_integration_session and is_integration_test:
        pytest.skip('skipped integration test')


# fixtures


@pytest.fixture
def bitcoin_core():
    return connectors.BitcoinCoreConnector(
        rpc_host='127.0.0.1',
        rpc_port=18332,
        rpc_username='testnet_user',
        rpc_password='testnet_pass',
    )
