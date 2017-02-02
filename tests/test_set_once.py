"""Test SetOnceDescriptor implementation"""
import pytest

from neoalchemy import Node, Property, Relationship
from neoalchemy.exceptions import ImmutableAttributeError


def test_property_set_once():
    prop = Property()
    with pytest.raises(ImmutableAttributeError):
        prop.type = int
    with pytest.raises(ImmutableAttributeError):
        prop.indexed = False
    with pytest.raises(ImmutableAttributeError):
        prop.unique = True
    with pytest.raises(ImmutableAttributeError):
        prop.required = 5
    with pytest.raises(ImmutableAttributeError):
        prop.primary_key = None
    with pytest.raises(ImmutableAttributeError):
        prop.read_only = "DON'T CHANGE ME"

    # Can change these b/c at this point they're still None
    prop.name = 'fred'
    prop.default = 5
    # Type checking is still performed
    with pytest.raises(ValueError):
        prop.obj = 5
    prop.obj = Node('x')

    with pytest.raises(ImmutableAttributeError):
        prop.name = 'bob'
    with pytest.raises(ImmutableAttributeError):
        prop.default = 9
    with pytest.raises(ImmutableAttributeError):
        prop.obj = Node('y')

    prop = Property(default=5, obj=Node('x'))
    with pytest.raises(ImmutableAttributeError):
        prop.default = 9
    with pytest.raises(ImmutableAttributeError):
        prop.obj = Node('y')

    with pytest.raises(ImmutableAttributeError):
        del prop.name
    with pytest.raises(ImmutableAttributeError):
        del prop.type
    with pytest.raises(ImmutableAttributeError):
        del prop.default
    with pytest.raises(ImmutableAttributeError):
        del prop.obj
    with pytest.raises(ImmutableAttributeError):
        del prop.unique
    with pytest.raises(ImmutableAttributeError):
        del prop.indexed
    with pytest.raises(ImmutableAttributeError):
        del prop.required
    with pytest.raises(ImmutableAttributeError):
        del prop.primary_key
    with pytest.raises(ImmutableAttributeError):
        del prop.read_only


def test_node_set_once():
    node = Node('x')
    with pytest.raises(ImmutableAttributeError):
        node.labels = list('abc')
    with pytest.raises(ImmutableAttributeError):
        node.type = 'y'
    with pytest.raises(ImmutableAttributeError):
        del node.labels
    with pytest.raises(ImmutableAttributeError):
        del node.type


def test_relationship_set_once():
    rel = Relationship(None)
    rel.type = 'X'
    rel.start_node = Node('x')
    rel.end_node = Node('y')
    with pytest.raises(ImmutableAttributeError):
        rel.directed = False
    with pytest.raises(ImmutableAttributeError):
        rel.type = 'Y'
    with pytest.raises(ImmutableAttributeError):
        rel.start_node = Node('a')
    with pytest.raises(ImmutableAttributeError):
        rel.end_node = Node('b')

    rel = Relationship('X')
    with pytest.raises(ImmutableAttributeError):
        rel.type = 'Y'

    rel = Relationship('X', Node('a'))
    with pytest.raises(ImmutableAttributeError):
        rel.start_node = Node('a')

    rel = Relationship('X', Node('a'), Node('b'))
    with pytest.raises(ImmutableAttributeError):
        rel.end_node = Node('a')

    with pytest.raises(ImmutableAttributeError):
        del rel.type
    with pytest.raises(ImmutableAttributeError):
        del rel.directed
    with pytest.raises(ImmutableAttributeError):
        del rel.start_node
    with pytest.raises(ImmutableAttributeError):
        del rel.end_node
