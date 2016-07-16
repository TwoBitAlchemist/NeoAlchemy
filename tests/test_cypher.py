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


def test_create_unique():
    user = NodeType('User')
    create = Create(user, unique=True)
    assert str(create) == 'CREATE UNIQUE (n:User)'
    assert not create.params


def test_create_nodetype_one_prop():
    user = NodeType('User', Property('name'))
    create = Create(user)
    assert str(create) == 'CREATE (n:User {name: {name_n}})'
    assert len(create.params) == 1
    assert create.params['name_n'] is None
    create = Create(user).set(name='Frank')
    assert str(create) == 'CREATE (n:User) SET n.name = {name_n}'
    assert len(create.params) == 1
    assert create.params['name_n'] == 'Frank'


def test_create_nodetype_two_props():
    user = NodeType('User', Property('name'), Property('age', type=int))
    create = Create(user)
    assert len(create.params) == 2
    assert create.params['name_n'] is None
    assert create.params['age_n'] is None
    create.set(name='Frank').compile()
    assert create.params['name_n'] == 'Frank'
    assert create.params['age_n'] is None
    create.set(age='29').compile()
    assert create.params['age_n'] == 29


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


def test_full_match():
    Person = NodeType('Person', Property('name'))
    match = (Match(Person, 'n')['KNOWS'](Person, 'm')
               .where(Person.name=='Alice', 'm'))
    assert str(match) == ('MATCH (n:Person)-[r1:KNOWS]->(m:Person)'
                          ' WHERE m.name = {name_m}')
    assert match.params['name_m'] == 'Alice'
    match.return_().order_by({'n': 'name'}).skip(1).limit(1)
    assert str(match) == '\n'.join(('MATCH (n:Person)-[r1:KNOWS]->(m:Person)'
                                    ' WHERE m.name = {name_m}',
                                    'RETURN * ORDER BY n.name ASC '
                                    'SKIP 1 LIMIT 1'))
    assert match.params['name_m'] == 'Alice'


def test_return():
    Person = NodeType('Person')
    match = Match(Person)
    query = 'MATCH (n:Person)'
    assert str(match.return_()) == '\n'.join((query, 'RETURN *'))
    assert str(match.return_('n')) == '\n'.join((query, 'RETURN n'))
    match &= Match(Person, 'm')
    query = '\n'.join((query, 'MATCH (m:Person)'))
    assert str(match.return_(['n', 'm'])) == '\n'.join((query, 'RETURN n, m'))
    assert str(match.return_({'n': 'name'})) == '\n'.join((query,
                                                           'RETURN n.name'))
    assert (str(match.return_({'n': ['x', 'y']})) == 
            '\n'.join((query, 'RETURN n.x, n.y')))
    try:
        assert (str(match.return_({'m': 'x', 'n': 'y'})) == 
                '\n'.join((query, 'RETURN n.y, m.x')))
    except AssertionError:
        assert (str(match.return_({'m': 'x', 'n': 'y'})) == 
                '\n'.join((query, 'RETURN m.x, n.y')))


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
                      Property('age', type=int))
    expected_match += ' AND n.age = {age_n}'
    match = (Match(Person)
                .where((Person.name=='Alice') &
                       (Person.hair_color=='red') &
                       (Person.age=='29')))
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


def test_arithmetic_cypher_expressions():
    Person = NodeType('Person', Property('age', type=int))

    match = Match(Person).where((Person.age + 5) == 23)
    assert str(match) == 'MATCH (n:Person) WHERE n.age + {param0} = {param1}'
    assert match.params['param0'] == 5
    assert match.params['param1'] == 23
    match = Match(Person).where((5 + Person.age) == 23)
    assert str(match) == 'MATCH (n:Person) WHERE n.age + {param0} = {param1}'
    assert match.params['param0'] == 5
    assert match.params['param1'] == 23

    match = Match(Person).where((Person.age - 4) == 13)
    assert str(match) == 'MATCH (n:Person) WHERE n.age - {param0} = {param1}'
    assert match.params['param0'] == 4
    assert match.params['param1'] == 13
    match = Match(Person).where((4 - Person.age) == 13)
    assert str(match) == 'MATCH (n:Person) WHERE {param0} - n.age = {param1}'
    assert match.params['param0'] == 4
    assert match.params['param1'] == 13

    match = Match(Person).where((Person.age * 5) == 23)
    assert str(match) == 'MATCH (n:Person) WHERE n.age * {param0} = {param1}'
    assert match.params['param0'] == 5
    assert match.params['param1'] == 23
    match = Match(Person).where((5 * Person.age) == 23)
    assert str(match) == 'MATCH (n:Person) WHERE n.age * {param0} = {param1}'
    assert match.params['param0'] == 5
    assert match.params['param1'] == 23

    match = Match(Person).where((Person.age / 4) == 13)
    assert str(match) == 'MATCH (n:Person) WHERE n.age / {param0} = {param1}'
    assert match.params['param0'] == 4
    assert match.params['param1'] == 13
    match = Match(Person).where((4 / Person.age) == 13)
    assert str(match) == 'MATCH (n:Person) WHERE {param0} / n.age = {param1}'
    assert match.params['param0'] == 4
    assert match.params['param1'] == 13

    match = Match(Person).where((Person.age % 4) == 13)
    assert str(match) == 'MATCH (n:Person) WHERE n.age % {param0} = {param1}'
    assert match.params['param0'] == 4
    assert match.params['param1'] == 13
    match = Match(Person).where((4 % Person.age) == 13)
    assert str(match) == 'MATCH (n:Person) WHERE {param0} % n.age = {param1}'
    assert match.params['param0'] == 4
    assert match.params['param1'] == 13

    match = Match(Person).where((Person.age ** 4) == 13)
    assert str(match) == 'MATCH (n:Person) WHERE n.age ^ {param0} = {param1}'
    assert match.params['param0'] == 4
    assert match.params['param1'] == 13
    match = Match(Person).where((4 ** Person.age) == 13)
    assert str(match) == 'MATCH (n:Person) WHERE {param0} ^ n.age = {param1}'
    assert match.params['param0'] == 4
    assert match.params['param1'] == 13
