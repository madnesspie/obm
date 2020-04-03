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
import marshmallow
from marshmallow import fields


class Transaction(marshmallow.Schema):
    txid = fields.String(required=True)
    from_address = fields.String(allow_none=True, required=True)
    to_address = fields.String(allow_none=True, required=True)
    amount = fields.Decimal(required=True)
    category = fields.String(allow_none=True, required=True)
    block_number = fields.Integer(allow_none=True, required=True)
    timestamp = fields.Integer(allow_none=True, required=True)
    fee = fields.Decimal(allow_none=True, required=True)
    info = fields.Dict(required=True)
