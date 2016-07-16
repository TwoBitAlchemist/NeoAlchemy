"""Schema ORM tests"""
from datetime import date, datetime
import pytest
import uuid

from neoalchemy import Node, Property


def test_property_type():
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


def test_property_default():
    def valid_uuid(id_):
        if id_ is None:
            return
        return str(uuid.UUID(str(id_)))

    def YYYYMMDD(date_str):
        if date_str is None:
            return
        return datetime.strptime(str(date_str), '%Y-%m-%d')

    class MyNode(Node):
        date = Property(type=YYYYMMDD, default=date.today)
        integer = Property(type=int, default=14)
        uuid = Property(type=valid_uuid, default=uuid.uuid4)

    my_node = MyNode()
    assert YYYYMMDD(my_node.date)
    assert my_node.integer == 14
    assert valid_uuid(my_node.uuid)
