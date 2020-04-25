.. OBM documentation master file, created by
   sphinx-quickstart on Mon Mar 23 12:59:03 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. role:: bash(code)
   :language: bash

Welcome to OBM's documentation!
===============================

Motivation
----------
There are a lot of cryprocurrencies and many of them maintain their own
blockchain. Essentially, blockchain is a database, therefore you can interact
with it in the same way as with the ordinary database. If you follow how the
database interacting tools evolved, you can see that at low-level there are
database adapters (such as psycopg2, pymongo, etc.) on top of which are built
more abstract and convenient ORMs/ODMs (sqlalchemy, mongo-engine, etc.)
Blockchain technology, that is still in its infancy, really lacks similar tools
for developers. The goal of this project is to become such a tool. It provides
both low-level adapters and high-level ORM-like API for interacting with
blockchain node. Also, it's worth clarifying, that ordinary databases have
already reached stable APIs unlike blockchain nodes that just provide scattered
JSON RPC or/and other non-standard API. OBM is trying to do typically things in
universal way. Thereby standardization and unification become the second
project goal.

Installation
------------

.. code-block:: bash

   pip install obm

Requirements
------------
- Python 3.8 or higher.
- (optional) bitcoin-core node
- (optional) geth node


Features
--------
- Async and sync top-level API
- BTC (bitcoin-core) and ETH (geth) support
- Implemented :bash:`list-transactions` for ETH
- Unified API for sending/receiving transactions, addresses creation and fee
  estimating

In future
`````````
- support of: ETH, ETC, DASH, BCH, LTC, ZEC, XEM, XRP, etc.

Is OBM production ready?
------------------------
The project is now under active development. Use at your own risk and lock
dependency version on minore.

.. Contributing
.. ------------
.. See CONTRIBUTING.md for instructions.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
