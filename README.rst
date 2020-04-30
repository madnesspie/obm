.. role:: bash(code)
   :language: bash
.. role:: raw-html(raw)
    :format: html

|

.. image:: https://raw.githubusercontent.com/madnesspie/obm/e310e12d5485a98bb3b6526ac71b5c5ccd702961/logo.svg
   :target: https://github.com/madnesspie/obm
   :align: center
   :width: 70%
   :alt: OBM logo

|
|
|
|

|travis| |pypi-version| |readthedocs| |code-style|

.. |travis| image:: https://travis-ci.org/madnesspie/obm.svg?branch=master
    :target: https://travis-ci.org/madnesspie/obm
    :alt: Travis CI Build Status

.. |pypi-version| image:: https://badge.fury.io/py/obm.svg
    :target: https://badge.fury.io/py/obm
    :alt: PyPI version

.. |readthedocs| image:: https://readthedocs.org/projects/obm/badge/?version=latest
    :target: https://obm.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. |code-style| image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black
    :alt: Code style: black

Motivation
==========
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

Resources
=========
- `Documentation <https://obm.readthedocs.io/>`_
- `Releases <https://github.com/madnesspie/obm/releases>`_

Installation
============

.. code-block:: bash

    pip install obm


Requirements
============
- Python 3.8 or higher.
- (optional) `bitcoin-core <https://bitcoincore.org/en/download/>`_ node
- (optional) `geth <https://geth.ethereum.org/downloads/>`_ node

Features
========
- Async and sync top-level API
- BTC (bitcoin-core) and ETH (geth) support
- Implemented :bash:`list-transactions` for ETH
- Unified API for sending/receiving transactions, addresses creation and fee
  estimating

Future features
---------------
- support for: ETH, ETC, DASH, BCH, LTC, ZEC, XEM, XRP, etc.

Is OBM production ready?
====================================================
The project is now under active development. Use at your own risk and lock
dependency version on minore.

Contributing
============
See `CONTRIBUTING.md <https://github.com/madnesspie/obm/blob/master/CONTRIBUTING.md>`_
for instructions.

Support the developer
=====================

Sponsors
--------
Special thanks for `Swapzilla <https://www.swapzilla.co/>`_ project that
paid me part of the development.

.. figure:: https://raw.githubusercontent.com/madnesspie/django-obm/d285241038bb8d325599e8c4dddb567468daae81/docs/swapzilla.jpeg
  :width: 100%
  :figwidth: image
  :alt: Swapzilla logo

You can also become the sponsor and get priority development of the features
you require. Just `contact me <https://github.com/madnesspie>`_.

Buy me a beer
-------------
.. code-block:: bash

    BTC 179B1vJ8LvAQ2r9ABNhp6kDE2yQZfm1Ng3
