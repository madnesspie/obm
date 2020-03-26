import marshmallow
from marshmallow import fields


class Transaction(marshmallow.Schema):
    txid = fields.String()
    address = fields.String()
    amount = fields.Float()
    category = fields.String()
    confirmations = fields.Integer()
    timestamp = fields.Integer(data_key="time")

    class Meta:
        unknown = marshmallow.EXCLUDE
