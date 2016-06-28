"""Cypher object tests"""
import pytest

from neoalchemy import NodeType, Property
from neoalchemy.cypher import Create, Match
from neoalchemy.cypher.base import CompileError


def test_create_nodetype_no_props():
    user = NodeType('User')
    create = Create(user)
    assert str(create) == 'CREATE (n:User)'
    assert not create.params


def test_create_nodetype_one_prop():
    user = NodeType('User', Property('name'))
    create = Create(user)
    assert str(create) == 'CREATE (n:User {name: {name}})'
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
    assert str(create) == 'CREATE (n:User:Person {name: {name}})'


def test_create_relation_to_nowhere():
    user = NodeType('User')
    create = Create(user)['KNOWS']
    with pytest.raises(CompileError):
        str(create)


def test_create_relationship():
    user = NodeType('User')
    create = Create(user)['KNOWS'](user)
    assert str(create) == 'CREATE (n:User)-[r0:KNOWS]->(n_1:User)'


def test_multiple_params():
    user = NodeType('User', Property('name'))
    create = Create(user)['KNOWS'](user)
    assert str(create) == ('CREATE (n:User {name: {name}})'
                           '-[r0:KNOWS]->(n_1:User {name: {name_1}})')
    assert 'name' in create.params
    assert 'name_1' in create.params


def test_multiple_named_params():
    user = NodeType('User', Property('name'))
    create = Create(user, 'n')['KNOWS'](user, 'm')
    assert str(create) == ('CREATE (n_n:User {name: {name_n}})'
                           '-[r0:KNOWS]->(n_m:User {name: {name_m}})')
    assert 'name_n' in create.params
    assert 'name_m' in create.params


def test_match_refcard_1():
    Person = NodeType('Person', Property('name'))
    match = (Match(Person, 'n')['KNOWS'](Person, 'm')
               .where(Person.name=='Alice', 'n'))
    assert str(match) == ('MATCH (n_n:Person)-[r0:KNOWS]->(n_m:Person)'
                          " WHERE n_n.name = 'Alice'")
    assert 'name_n' in match.params
    assert 'name_m' in match.params


def test_matching_super_simple_stuff():
    Person = NodeType('Person')
    match = Match(Person, 'n')(Person, 'm')
    assert str(match) == 'MATCH (n_n:Person)-[r0]->(n_m:Person)'
    match = Match(Person, 'n')[''](Person, 'm')
    assert str(match) == 'MATCH (n_n:Person)-[r0]->(n_m:Person)'
    match = Match(Person, 'n')[None](Person, 'm')
    assert str(match) == 'MATCH (n_n:Person)-[r0]->(n_m:Person)'


def test_optional_match():
    Person = NodeType('Person')
    match = Match(Person, 'n', optional=True)(Person, 'm')
    assert str(match) == 'OPTIONAL MATCH (n_n:Person)-[r0]->(n_m:Person)'
