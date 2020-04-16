from obm import connectors


def test_supported_currencies():
    assert isinstance(connectors.SUPPORTED_CURRENCIES, list)
    assert len(connectors.SUPPORTED_CURRENCIES) > 1
