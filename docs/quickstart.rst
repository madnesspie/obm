.. role:: bash(code)
   :language: bash
.. role:: python(code)
   :language: python


Quickstart
==========
There are two layers in :bash:`OBM` architecture. The top-level is
:bash:`obm.models`, that provide unified API and should be enough in most cases.
The second one is low-level :bash:`obm.connectors`, that contains connectors
with non-unified and unified for each node that supported by :bash:`obm`.

.. note::
    This guide uses python built-in async REPL to show asynchronous API
    features. You can launch it using command :bash:`python -m asyncio` (Python
    3.8 or higher).

Models
------

Create a model
````````````````
.. code-block:: python

    >>> import asyncio
    >>> from obm import models
    >>> btc = models.Node(
    ...     name="bitcoin-core",
    ...     rpc_port=18332,
    ...     rpc_username="testnet_user",
    ...     rpc_password="testnet_pass",
    ... )
    >>> eth = models.Node(
    ...     name="geth",
    ...     rpc_port=8545,
    ... )

Create address
``````````````
.. code-block:: python

    >>> await btc.create_address()
    '2N1Gbn5dqQxxD443Se9moXBaafGLvKCweop'
    >>> await eth.create_address()
    '0x8a9c181caa4a1273e46a306309e806e2d61fc560'

Send transactions
`````````````````
.. code-block:: python

    >>> await btc.send_transaction(
    ...     amount=0.00001,
    ...     to_address='2NAmne8BsSXWbV5iStkVzL4vW7Z4F6a5o68',
    ...     subtract_fee_from_amount=True,
    ... )
    {
        "txid": "cc8c9f7a86261fcb00d68b62073c740b8a0e14079d67e44fd726e0de2954c69a",
        "from_address": "2NAmne8BsSXWbV5iStkVzL4vW7Z4F6a5o68",
        "to_address": "2NAmne8BsSXWbV5iStkVzL4vW7Z4F6a5o68",
        "amount": Decimal("0.00000866"),
        "fee": Decimal("0.00000134"),
        "block_number": None,
        "category": "oneself",
        "timestamp": 1588076404,
        "info": {...},
    }
    >>> await eth.send_transaction(
    ...     amount=0.00005,
    ...     from_address='0xe1082e71f1ced0efb0952edd23595e4f76840128',
    ...     to_address='0xb610de1be67b10c746afec8fe74ad14d97e34146',
    ...     subtract_fee_from_amount=True,
    ...     password="abc",
    ... )
    {
        "txid": "0x4831820db0de1aad336c7a083b2504ad0b91eba293e5d7a6fa3bef49f660766c",
        "from_address": "0xe1082e71f1ced0efb0952edd23595e4f76840128",
        "to_address": "0xb610de1be67b10c746afec8fe74ad14d97e34146",
        "amount": Decimal("0.000029"),
        "fee": Decimal("0.000021"),
        "block_number": None,
        "category": "oneself",
        "timestamp": None,
        "info": {...},
    }
