import web3


def to_wei(value):
    return web3.Web3.toWei(value, "ether")


def to_hex(value):
    return web3.Web3.toHex(value)


def to_int(value):
    return web3.Web3.toInt(hexstr=value)
