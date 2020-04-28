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

Models
------

Create the model
````````````````
.. code-block:: python

    >>> from obm.sync import models
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

    >>> btc.create_address()
    '2N1Gbn5dqQxxD443Se9moXBaafGLvKCweop'
    >>> eth.create_address()
    '0x8a9c181caa4a1273e46a306309e806e2d61fc560'
