from decimal import Decimal
import uuid

from neoalchemy import OneToManyRelation, Property
from neoalchemy.validators import UUID

from .graph import OGMTestClass


def money(value):
    if value is None:
        return
    return '%.2f' % Decimal(value)


class OrderItem(OGMTestClass):
    line_item = Property(primary_key=True)
    price = Property(type=money, primary_key=True)


class Order(OGMTestClass):
    id = Property(type=UUID, default=uuid.uuid4, primary_key=True,
                  indexed=True)
    items = OneToManyRelation('HAS_ITEM', restrict_types=(OrderItem,),
                              backref='order')
