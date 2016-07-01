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
    assert str(create) == 'CREATE (n:User {name: {name_n}})'
    assert len(create.params) == 1
    assert 'name_n' in create.params


def test_create_nodetype_two_props():
    user = NodeType('User', Property('name'), Property('age'))
    create = Create(user)
    assert len(create.params) == 2
    assert 'name_n' in create.params
    assert 'age_n' in create.params


def test_create_nodetype_two_labels():
    user = NodeType('User', Property('name'), extra_labels=('Person',))
    create = Create(user)
    assert str(create) == 'CREATE (n:User:Person {name: {name_n}})'


def test_create_relation_to_nowhere():
    user = NodeType('User')
    create = Create(user)['KNOWS']
    with pytest.raises(CompileError):
        str(create)


def test_create_relationship():
    user = NodeType('User')
    create = Create(user)['KNOWS'](user)
    assert str(create) == 'CREATE (n:User)-[r1:KNOWS]->(n1:User)'


def test_multiple_params():
    user = NodeType('User', Property('name'))
    create = Create(user)['KNOWS'](user)
    assert str(create) == ('CREATE (n:User {name: {name_n}})'
                           '-[r1:KNOWS]->(n1:User {name: {name_n1}})')
    assert 'name_n' in create.params
    assert 'name_n1' in create.params


def test_multiple_named_params():
    user = NodeType('User', Property('name'))
    create = Create(user, 'n')['KNOWS'](user, 'm')
    assert str(create) == ('CREATE (n:User {name: {name_n}})'
                           '-[r1:KNOWS]->(m:User {name: {name_m}})')
    assert 'name_n' in create.params
    assert 'name_m' in create.params


def test_match_with_where_expressions():
    Person = NodeType('Person', Property('name'))
    match = (Match(Person, 'n')['KNOWS'](Person, 'm')
               .where(Person.name=='Alice', 'n'))
    assert str(match) == ('MATCH (n:Person)-[r1:KNOWS]->(m:Person)'
                          " WHERE n.name = {name_n}")
    assert match.params == {'name_n': 'Alice'}


def test_matching_super_simple_stuff():
    Person = NodeType('Person')
    match = Match(Person, 'n')(Person, 'm')
    assert str(match) == 'MATCH (n:Person)-[r1]->(m:Person)'
    match = Match(Person, 'n')[''](Person, 'm')
    assert str(match) == 'MATCH (n:Person)-[r1]->(m:Person)'
    match = Match(Person, 'n')[None](Person, 'm')
    assert str(match) == 'MATCH (n:Person)-[r1]->(m:Person)'


def test_optional_match():
    Person = NodeType('Person')
    match = Match(Person, 'n', optional=True)(Person, 'm')
    assert str(match) == 'OPTIONAL MATCH (n:Person)-[r1]->(m:Person)'


def test_logical_cypher_expressions():
    Person = NodeType('Person', Property('name'))
    match = Match(Person).where(Person.name=='Alice')
    assert str(match) == 'MATCH (n:Person) WHERE n.name = {name_n}'
    assert match.params['name_n'] == 'Alice'
    match = Match(Person).where(Person.name!='Alice')
    assert str(match) == 'MATCH (n:Person) WHERE n.name <> {name_n}'
    assert match.params['name_n'] == 'Alice'
    match = Match(Person).where(Person.name>='Alice')
    assert str(match) == 'MATCH (n:Person) WHERE n.name >= {name_n}'
    assert match.params['name_n'] == 'Alice'
    match = Match(Person).where(Person.name<='Alice')
    assert str(match) == 'MATCH (n:Person) WHERE n.name <= {name_n}'
    assert match.params['name_n'] == 'Alice'
    match = Match(Person).where(Person.name<'Alice')
    assert str(match) == 'MATCH (n:Person) WHERE n.name < {name_n}'
    assert match.params['name_n'] == 'Alice'
    match = Match(Person).where(Person.name>'Alice')
    assert str(match) == 'MATCH (n:Person) WHERE n.name > {name_n}'
    assert match.params['name_n'] == 'Alice'


def test_complex_logical_cypher_expressions():
    Person = NodeType('Person', Property('name'), Property('hair_color'))
    expected_match = ('MATCH (n:Person) WHERE n.name = {name_n} '
                      'AND n.hair_color = {hair_color_n}')

    match = (Match(Person)
                .where(Person.name=='Alice')
                .where(Person.hair_color=='red'))
    assert str(match) == expected_match
    assert match.params == {'name_n': 'Alice', 'hair_color_n': 'red'}

    match = (Match(Person)
                .where((Person.name=='Alice') & (Person.hair_color=='red')))
    assert str(match) == expected_match
    assert match.params == {'name_n': 'Alice', 'hair_color_n': 'red'}

    Person = NodeType('Person', Property('name'), Property('hair_color'),
                      Property('age'))
    expected_match += ' AND n.age = {age_n}'
    match = (Match(Person)
                .where((Person.name=='Alice') &
                       (Person.hair_color=='red') &
                       (Person.age==29)))
    assert str(match) == expected_match
    assert match.params == {'name_n': 'Alice', 'hair_color_n': 'red',
                            'age_n': 29}

    match = (Match(Person)
                .where(Person.name=='Alice')
                .where(Person.hair_color=='red')
                .where(Person.age==29))
    assert str(match) == expected_match
    assert match.params == {'name_n': 'Alice', 'hair_color_n': 'red',
                            'age_n': 29}

    expected_match = 'OR'.join(expected_match.rsplit('AND', 1))
    match = (Match(Person)
                .where((Person.name=='Alice') &
                       (Person.hair_color=='red') |
                       (Person.age==29)))
    assert str(match) == expected_match
    assert match.params == {'name_n': 'Alice', 'hair_color_n': 'red',
                            'age_n': 29}

    match = (Match(Person)
                .where(Person.name=='Alice')
                .where(Person.hair_color=='red')
                .where(Person.age==29, or_=True))
    assert str(match) == expected_match
    assert match.params == {'name_n': 'Alice', 'hair_color_n': 'red',
                            'age_n': 29}


@pytest.mark.xfail
def test_arithmetic_cypher_expressions():
    Person = NodeType('Person', Property('age'))
    match = Match(Person).where((Person.age + 5) == 23)
    assert str(match) == 'MATCH (n:Person) WHERE n.age + {param0} = {param1}'
    assert match.params == {'param0': 5, 'param1': 23}
