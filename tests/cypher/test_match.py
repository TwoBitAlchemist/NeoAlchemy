"""Cypher Match tests"""
from neoalchemy import Match, Merge, Node, Property, Relationship


def test_full_match():
    expected_stmt = [
        'MATCH (m:`Person`)',
        '    WHERE m.name = {m_name}',
        'MATCH (n:`Person`)',
        '    WHERE n.name = {n_name}',
        'MATCH (m)-[rel:`KNOWS`]->(n)',
    ]
    person_m = Node('Person', name='Alice', var='m').bind('name')
    person_n = person_m.copy(name='Bob', var='n')
    knows = Relationship('KNOWS', person_m, person_n)
    match = Match(person_m) & Match(person_n) & Match(knows)
    assert str(match) == '\n'.join(expected_stmt)
    assert len(match.params) == 2
    assert 'm_name' in match.params
    assert match.params['m_name'] == 'Alice'
    assert 'n_name' in match.params
    assert match.params['n_name'] == 'Bob'
    match.return_().order_by(person_n['name']).skip(1).limit(1)
    expected_stmt += [
        'RETURN *',
        'ORDER BY n.name',
        'SKIP 1',
        'LIMIT 1',
    ]
    assert str(match) == '\n'.join(expected_stmt)
    assert len(match.params) == 2
    assert 'm_name' in match.params
    assert match.params['m_name'] == 'Alice'
    assert 'n_name' in match.params
    assert match.params['n_name'] == 'Bob'
    expected_stmt[-3] += ' DESC'
    for _ in range(3):
        match.pop()
    match.order_by(person_n['name'], desc=True).skip(1).limit(1)
    assert str(match) == '\n'.join(expected_stmt)
    assert len(match.params) == 2
    assert 'm_name' in match.params
    assert match.params['m_name'] == 'Alice'
    assert 'n_name' in match.params
    assert match.params['n_name'] == 'Bob'


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


def test_cypher_methods():
    n = Node('Person', name='Mr. N', var='n')
    match = Match(n)
    query = 'MATCH (n:`Person`)'
    assert str(match.delete(n)) == '\n'.join((query, 'DELETE n'))
    match.pop()
    assert str(match.delete(n['name'])) == '\n'.join((query, 'DELETE n.name'))
    match.pop()
    assert str(match.delete(n, detach=True)) == '\n'.join((query,
                                                           'DETACH DELETE n'))
    match.pop()
    assert str(match.remove(n['name'])) == '\n'.join((query, 'REMOVE n.name'))
    match.pop()
    assert (str(match.delete(n).with_(n).return_(n['name'])) ==
            '\n'.join((query, 'DELETE n', 'WITH n', 'RETURN n.name')))


def test_union_and_union_all():
    n = Node('Person', name='Mr. N', var='n')
    m = n.copy(var='m', name='Mrs. M')
    expected_stmt = [
        'MATCH (n:`Person`)',
        'UNION',
        'MATCH (m:`Person`)',
    ]
    assert str(Match(n) ^ Match(m)) == '\n'.join(expected_stmt)
    expected_stmt[1] += ' ALL'
    assert str(Match(n) | Match(m)) == '\n'.join(expected_stmt)


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


def test_where_and_set():
    person = Node('Person', name='Ali', age=Property(value=29, type=int),
                  hair_color='red', var='n')
    expected_match = [
        'MATCH (n:`Person`)',
        '    WHERE n.name = {n_name}',
    ]
    match = Match(person.bind('name'))
    assert str(match) == '\n'.join(expected_match)
    assert len(match.params) == 1
    assert 'n_name' in match.params
    assert match.params['n_name'] == 'Ali'
    expected_match = [
        'MATCH (n:`Person`)',
        '    WHERE n.name = {n_name} AND n.age = {n_age}',
    ]
    match = Match(person.bind('name', 'age'))
    try:
        assert str(match) == '\n'.join(expected_match)
    except AssertionError:
        expected_match.pop()
        expected_match.append(
            '    WHERE n.age = {n_age}'
            ' AND n.name = {n_name}'
        )
        assert str(match) == '\n'.join(expected_match)
    assert len(match.params) == 2
    assert 'n_name' in match.params
    assert match.params['n_name'] == 'Ali'
    assert 'n_age' in match.params
    assert match.params['n_age'] == 29
    match.set(person['age'] == 30)
    expected_match.append('    SET n.age = {param0}')
    assert str(match) == '\n'.join(expected_match)
    assert len(match.params) == 3
    assert 'n_name' in match.params
    assert match.params['n_name'] == 'Ali'
    assert 'n_age' in match.params
    assert match.params['n_age'] == 29
    assert 'param0' in match.params
    assert match.params['param0'] == 30
    match.set(person['name'] == 'Alison')
    expected_match.append('    SET n.name = {param1}')
    assert str(match) == '\n'.join(expected_match)
    assert len(match.params) == 4
    assert 'n_name' in match.params
    assert match.params['n_name'] == 'Ali'
    assert 'n_age' in match.params
    assert match.params['n_age'] == 29
    assert 'param0' in match.params
    assert match.params['param0'] == 30
    assert 'param1' in match.params
    assert match.params['param1'] == 'Alison'


def test_where_and_or():
    person = Node('Person', name='Ali', age=Property(value=29, type=int),
                  hair_color='red', var='n')
    expected_match = [
        'MATCH (n:`Person`)',
        '    WHERE n.name = {n_name}',
    ]
    match = Match(person.bind('name'))
    assert str(match) == '\n'.join(expected_match)
    assert len(match.params) == 1
    assert 'n_name' in match.params
    assert match.params['n_name'] == 'Ali'
    match.where(person['age']) == 29
    expected_match.append('      AND n.age = {n_age}')
    assert str(match) == '\n'.join(expected_match)
    assert len(match.params) == 2
    assert 'n_name' in match.params
    assert match.params['n_name'] == 'Ali'
    assert 'n_age' in match.params
    assert match.params['n_age'] == 29
    match = Match(person.bind('name'))
    match.where(person['age'], or_=True) == 29
    expected_match.pop()
    expected_match.append('       OR n.age = {n_age}')
    assert str(match) == '\n'.join(expected_match)
    assert len(match.params) == 2
    assert 'n_name' in match.params
    assert match.params['n_name'] == 'Ali'
    assert 'n_age' in match.params
    assert match.params['n_age'] == 29


def test_merge():
    kev = Node('Person', name='Kevin', var='kev').bind('name')
    ali = Node('Person', name='Ali', var='ali').bind('name')
    rel = Relationship('LOVES', kev, ali, duration='forever').bind('duration')
    expected_stmt = [
        'MATCH (kev:`Person`)',
        '    WHERE kev.name = {kev_name}',
        'MATCH (ali:`Person`)',
        '    WHERE ali.name = {ali_name}',
        'MERGE (kev)-[rel:`LOVES` {duration: {rel_duration}}]->(ali)'
    ]
    query = Match(kev) & Match(ali) & Merge(rel)
    assert str(query) == '\n'.join(expected_stmt)
    assert len(query.params) == 3
    assert 'kev_name' in query.params
    assert query.params['kev_name'] == 'Kevin'
    assert 'ali_name' in query.params
    assert query.params['ali_name'] == 'Ali'
    assert 'rel_duration' in query.params
    assert query.params['rel_duration'] == 'forever'


def test_merge_on_create_on_match():
    person = Node('Person', name=Property())
    merge = (
        Merge(person)
            .on_create()
                .set(person['name'] == 'Fred')
            .on_match()
                .set(person['name'] == 'Bob')
    )
    expected_stmt = '\n'.join((
        'MERGE (node:`Person`)',
        'ON CREATE',
        '    SET node.name = {node_name}',
        'ON MATCH',
        '    SET node.name = {param0}'
    ))
    assert str(merge) == expected_stmt
    assert len(merge.params) == 2
    assert 'node_name' in merge.params
    assert merge.params['node_name'] == 'Fred'
    assert 'param0' in merge.params
    assert merge.params['param0'] == 'Bob'
