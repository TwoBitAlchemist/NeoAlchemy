"""Schema ORM tests"""
from datetime import datetime
import pytest
import uuid

from neoalchemy import Node, Property


def test_property_type_and_default():
    def valid_uuid(id_):
        if id_ is None:
            return
        return str(uuid.UUID(str(id_)))

    def YYYYMMDD(date_str):
        if date_str is None:
            return
        return datetime.strptime(str(date_str), '%Y-%m-%d')

    class MyNode(Node):
        date = Property(type=YYYYMMDD)
        string = Property()
        integer = Property(type=int)
        uuid = Property(type=valid_uuid)

    my_node = MyNode()
    assert my_node.date is None
    assert my_node.string is None
    assert my_node.integer is None
    assert my_node.uuid is None

    with pytest.raises(ValueError):
        my_node.date = 123
    my_node.date = '1987-07-12'
    assert my_node.date.year == 1987
    assert my_node.date.month == 7
    assert my_node.date.day == 12
    my_node.string = 1
    assert my_node.string == '1'
    my_node.integer = '1'
    assert my_node.integer == 1
    with pytest.raises(ValueError):
        my_node.uuid = 5
    my_node.uuid = uuid.uuid4()
