"""Schema object tests"""
import pytest

from neoalchemy import Node, Property


def test_simple_labeled_node():
    node = Node('Node')
    assert node.labels == ('Node',)
    # cannot reset label once created
    with pytest.raises(AttributeError):
        node.labels = ('bob',)
    assert not node.schema


def test_node_one_index():
    person = Node('Person', name=Property(indexed=True))
    assert person.schema == ['INDEX ON :Person(name)']
    assert person['name'].indexed
    assert not person['name'].unique
    assert not person['name'].required


def test_node_one_unique():
    person = Node('Person', SSN=Property(unique=True))
    assert person.schema == ['CONSTRAINT ON ( person:Person ) '
                             'ASSERT person.SSN IS UNIQUE']
    assert person['SSN'].indexed
    assert person['SSN'].unique
    assert not person['SSN'].required


def test_node_one_required():
    person = Node('Person', name=Property(required=True))
    assert person.schema == ['CONSTRAINT ON ( person:Person ) '
                             'ASSERT exists(person.name)']
    assert not person['name'].indexed
    assert not person['name'].unique
    assert person['name'].required


def test_node_one_required_and_indexed():
    person = Node('Person', name=Property(required=True, indexed=True))
    assert person.schema == ['INDEX ON :Person(name)',
                             'CONSTRAINT ON ( person:Person ) '
                             'ASSERT exists(person.name)']
    assert person['name'].indexed
    assert not person['name'].unique
    assert person['name'].required


def test_node_one_required_and_unique():
    person = Node('Person', name=Property(required=True, unique=True))
    assert person.schema == ['CONSTRAINT ON ( person:Person ) '
                             'ASSERT person.name IS UNIQUE',
                             'CONSTRAINT ON ( person:Person ) '
                             'ASSERT exists(person.name)']
    assert person['name'].indexed
    assert person['name'].unique
    assert person['name'].required
