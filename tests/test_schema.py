"""Schema object tests"""
import pytest

from neoalchemy import NodeType, Property


def test_simple_labeled_node():
    with pytest.raises(TypeError):  # no label
        Node = NodeType()
    Node = NodeType('Node')
    assert Node.label == 'Node'
    # cannot reset label once created
    with pytest.raises(AttributeError):
        Node.label = 'bob'
    assert not Node.schema


def test_invalid_property():
    with pytest.raises(TypeError):  # requires Property object, not str
        Person = NodeType('Person', 'xyz')


def test_node_duplicate_property():
    with pytest.raises(ValueError):
        Person = NodeType('Person', Property('name'), Property('name'))


def test_node_one_index():
    Person = NodeType('Person', Property('name', indexed=True))
    assert Person.schema == 'CREATE INDEX ON :Person(name)'
    assert Person.name.indexed
    assert not Person.name.unique
    assert not Person.name.required


def test_node_one_unique():
    Person = NodeType('Person', Property('SSN', unique=True))
    assert Person.schema == ('CREATE CONSTRAINT ON (node:Person) '
                             'ASSERT node.SSN IS UNIQUE')
    assert Person.SSN.indexed
    assert Person.SSN.unique
    assert not Person.SSN.required


def test_node_one_required():
    Person = NodeType('Person', Property('name', required=True))
    assert Person.schema == ('CREATE CONSTRAINT ON (node:Person) '
                             'ASSERT exists(node.name)')
    assert not Person.name.indexed
    assert not Person.name.unique
    assert Person.name.required


def test_node_one_required_and_indexed():
    Person = NodeType('Person', Property('name', required=True, indexed=True))
    assert Person.schema == ('CREATE INDEX ON :Person(name)\n'
                             'CREATE CONSTRAINT ON (node:Person) '
                             'ASSERT exists(node.name)')
    assert Person.name.indexed
    assert not Person.name.unique
    assert Person.name.required


def test_node_one_required_and_unique():
    Person = NodeType('Person', Property('name', required=True, unique=True))
    assert Person.schema == ('CREATE CONSTRAINT ON (node:Person) '
                             'ASSERT node.name IS UNIQUE\n'
                             'CREATE CONSTRAINT ON (node:Person) '
                             'ASSERT exists(node.name)')
    assert Person.name.indexed
    assert Person.name.unique
    assert Person.name.required
