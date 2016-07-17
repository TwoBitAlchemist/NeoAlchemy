"""Schema ORM tests"""
from datetime import date
import uuid

import pytest

from neoalchemy import Node, Property
from neoalchemy.types import valid_uuid, isodate


def test_property_type():
    class MyNode(Node):
        date = Property(type=isodate)
        string = Property()
        integer = Property(type=int)
        uuid = Property(type=valid_uuid)

    my_node = MyNode()
    assert my_node.date is None
    assert my_node.string is None
    assert my_node.integer is None
    assert my_node.uuid is None

    with pytest.raises(ValueError):
        my_node.date = 'rutabaga'
    my_node.date = '1987-07-12'
    assert my_node.date == '1987-07-12'
    my_node.string = 1
    assert my_node.string == '1'
    my_node.integer = '1'
    assert my_node.integer == 1
    with pytest.raises(ValueError):
        my_node.uuid = 5
    my_node.uuid = uuid.uuid4()


def test_property_default():
    class MyNode(Node):
        date = Property(type=isodate, default=date.today)
        integer = Property(type=int, default=14)
        uuid = Property(type=valid_uuid, default=uuid.uuid4)

    my_node = MyNode()
    assert isodate(my_node.date)
    assert my_node.integer == 14
    assert valid_uuid(my_node.uuid)
