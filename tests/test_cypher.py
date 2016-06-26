"""Cypher object tests"""
import pytest

from neoalchemy import NodeType, Property
from neoalchemy.cypher import Create
from neoalchemy.cypher.base import CompileError


def test_create_nodetype_no_props():
    user = NodeType('User')
    create = Create(user)
    assert str(create) == 'CREATE (node:User)'
    assert not create.params


def test_create_nodetype_one_prop():
    user = NodeType('User', Property('name'))
    create = Create(user)
    assert str(create) == 'CREATE (node:User {name: {name}})'
    assert len(create.params) == 1
    assert 'name' in create.params


def test_create_nodetype_two_props():
    user = NodeType('User', Property('name'), Property('age'))
    create = Create(user)
    assert len(create.params) == 2
    assert 'name' in create.params
    assert 'age' in create.params


def test_create_nodetype_two_labels():
    user = NodeType('User', Property('name'), extra_labels=('Person',))
    create = Create(user)
    assert str(create) == 'CREATE (node:User:Person {name: {name}})'


def test_create_relation_to_nowhere():
    user = NodeType('User')
    create = Create(user)['KNOWS']
    with pytest.raises(CompileError):
        str(create)


def test_create_relationship():
    user = NodeType('User')
    create = Create(user)['KNOWS'](user)
    assert str(create) == 'CREATE (node:User)-[:KNOWS]->(node_1:User)'
