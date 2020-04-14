import pytest

from obm import utils


@pytest.mark.research
@pytest.mark.integration
async def test_estimated_gas_does_not_depend_on_amount(geth):
    addresses = {
        # In-wallet address
        "from": "0xe1082e71f1ced0efb0952edd23595e4f76840128",
        # Random address
        "to": "0x81b7E08F65Bdf5648606c89998A9CC8164397647",
    }
    small_amount = await geth.rpc_eth_estimate_gas(
        {
            **addresses,
            "value": utils.to_hex(utils.to_wei(0.00001)),
        }
    )
    big_amount = await geth.rpc_eth_estimate_gas(
        {
            **addresses,
            "value": utils.to_hex(utils.to_wei(10)),
        }
    )
    without_amount = await geth.rpc_eth_estimate_gas(addresses)
    assert small_amount == big_amount == without_amount
