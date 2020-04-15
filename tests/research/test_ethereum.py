import pytest

from obm.connectors import ethereum


@pytest.mark.research
@pytest.mark.integration
async def test_estimate_gas_dependency_from_params(geth):
    """Implements the research of fee estimating from input params.

    How you can see, if we talk about non-contract addresses, estimated gas
    value depends only on the presence or absence of 'to' address.
    """
    # TODO: Study contract addresses.
    addresses = {
        # In-wallet address
        "from": "0xe1082e71f1ced0efb0952edd23595e4f76840128",
        # Random address
        "to": "0x81b7E08F65Bdf5648606c89998A9CC8164397647",
    }
    params_sets = [
        addresses,
        {**addresses, "value": ethereum.to_hex(ethereum.to_wei(0.00001))},
        {**addresses, "value": ethereum.to_hex(ethereum.to_wei(10))},
        {"to": addresses["to"]},
        {
            **addresses,
            "value": ethereum.to_hex(ethereum.to_wei(10)),
            "gasPrice": await geth.rpc_eth_gas_price(),
        },        {
            **addresses,
            "value": ethereum.to_hex(ethereum.to_wei(10)),
            "gas": '0x5208',  # 21000 wei or standard estimate
        },
        {
            **addresses,
            "value": ethereum.to_hex(ethereum.to_wei(10)),
            "gasPrice": await geth.rpc_eth_gas_price(),
            "gas": '0xcf08',  # 53000 wei or estimate without from address
        },
    ]
    fees = {await geth.rpc_eth_estimate_gas(i) for i in params_sets}
    assert len(fees) == 1
    fee = fees.pop()
    fee_without_from = await geth.rpc_eth_estimate_gas(
        {"from": addresses["from"]}
    )
    # Outcomes:
    # 1) If you do not provide the 'to' address the fee became greather
    # more than 2 times.
    # 2) Other params just ignored.
    assert fee * 2 < fee_without_from
