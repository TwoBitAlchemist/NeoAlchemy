"""Cypher Match tests"""
from neoalchemy import Match, Node, Property, Relationship


def test_full_match():
    expected_stmt = (
        'MATCH (m:`Person`)\n'
        '    WHERE m.name = {m_name}\n'
        'MATCH (n:`Person`)\n'
        'MATCH (m)-[rel:`KNOWS`]->(n)'
    )
    person_m = Node('Person', name='Alice', var='m').bind('name')
    person_n = person_m.copy(var='n')
    knows = Relationship('KNOWS', person_m, person_n)
    match = Match(person_m) & Match(person_n) & Match(knows)
    assert str(match) == expected_stmt
    assert len(match.params) == 1
    assert 'm_name' in match.params
    assert match.params['m_name'] == 'Alice'
    match.return_().order_by(person_n['name']).skip(1).limit(1)
    expected_stmt += (
        '\n'
        'RETURN *\n'
        'ORDER BY n.name\n'
        'SKIP 1\n'
        'LIMIT 1'
    )
    assert str(match) == expected_stmt
    assert len(match.params) == 1
    assert 'm_name' in match.params
    assert match.params['m_name'] == 'Alice'


def test_return():
    n = Node('Person', name=Property(), x=Property(), y=Property(), var='n')
    match = Match(n)
    query = 'MATCH (n:`Person`)'
    assert str(match.return_()) == '\n'.join((query, 'RETURN *'))
    match.pop()
    assert str(match.return_(n)) == '\n'.join((query, 'RETURN n'))
    match.pop()
    m = Node('Person', x=Property(), var='m')
    match &= Match(m)
    query = '\n'.join((query, 'MATCH (m:`Person`)'))
    assert str(match.return_(n, m)) == '\n'.join((query, 'RETURN n, m'))
    match.pop()
    assert str(match.return_(n['name'])) == '\n'.join((query,
                                                       'RETURN n.name'))
    match.pop()
    assert str(match.return_(n['x'], n['y'])) == '\n'.join((query,
                                                            'RETURN n.x, n.y'))
    match.pop()
    assert str(match.return_(m['x'], n['y'])) == '\n'.join((query,
                                                            'RETURN m.x, n.y'))


def test_matching_anonymous_relationship():
    person_m = Node('Person', var='m')
    person_n = person_m.copy(var='n')
    rel = Relationship(None, person_m, person_n)
    match = Match(rel)
    assert str(match) == 'MATCH (m)-[rel]->(n)'


def test_optional_match():
    person_m = Node('Person', var='m')
    person_n = person_m.copy(var='n')
    rel = Relationship(None, person_m, person_n)
    match = Match(rel, optional=True)
    assert str(match) == 'OPTIONAL MATCH (m)-[rel]->(n)'
