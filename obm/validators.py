# Copyright 2020 Alexander Polishchuk
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
from typing import Type

from obm import connectors, exceptions


def validate_node_is_supported(
    name: str, error_cls: Type[Exception] = exceptions.NodeUnsupportedError
) -> str:
    supported_nodes = list(connectors.MAPPING)
    if name not in supported_nodes:
        raise error_cls(f"Unsupported node. Available only: {supported_nodes}")
    return name


def validate_currency_is_supported(
    name: str, error_cls: Type[Exception] = exceptions.CurrencyUnsupportedError
) -> str:
    if name not in connectors.SUPPORTED_CURRENCIES:
        raise error_cls(
            f"Unsupported currency. Available only: "
            f"{connectors.SUPPORTED_CURRENCIES}"
        )
    return name
