"""Graph (Connection Class) Tests"""
import pytest

from neoalchemy import Graph, NodeType, Property
from tests.graph_test_settings import *
from tests.graph_test_settings import __TEST_LABEL__


def test_default_connection():
    graph = Graph()
    assert graph.driver.url == 'bolt://localhost'
    assert graph.driver.host == 'localhost'
    assert graph.driver.port is None
    assert graph.driver.config['auth'].scheme == 'basic'
    assert graph.driver.config['auth'].principal == 'neo4j'
    assert graph.driver.config['auth'].credentials == 'neo4j'


def test_http_connection():
    with pytest.warns(UserWarning):
        graph = Graph('http://localhost')
    assert graph.driver.url == 'bolt://localhost'
    assert graph.driver.host == 'localhost'
    assert graph.driver.port is None
    assert graph.driver.config['auth'].scheme == 'basic'
    assert graph.driver.config['auth'].principal == 'neo4j'
    assert graph.driver.config['auth'].credentials == 'neo4j'


def test_auth_token_in_connection():
    graph = Graph('bolt://user:pass@localhost')
    assert graph.driver.url == 'bolt://localhost'
    assert graph.driver.host == 'localhost'
    assert graph.driver.port is None
    assert graph.driver.config['auth'].scheme == 'basic'
    assert graph.driver.config['auth'].principal == 'user'
    assert graph.driver.config['auth'].credentials == 'pass'


def test_full_connection_string():
    graph = Graph('bolt://user:pass@localhost:7474')
    assert graph.driver.url == 'bolt://localhost:7474'
    assert graph.driver.host == 'localhost'
    assert graph.driver.port == 7474
    assert graph.driver.config['auth'].scheme == 'basic'
    assert graph.driver.config['auth'].principal == 'user'
    assert graph.driver.config['auth'].credentials == 'pass'


@clears_graph
def test_query_and_delete_all():
    graph = test_graph
    graph.delete_all()
    graph.query('CREATE (p:Person {name: "Bob"})')
    all_nodes = list(graph.query.all())
    assert len(all_nodes) == 1
    assert len(all_nodes[0]) == 1
    assert all_nodes[0][0]['name'] == 'Bob'
    graph.delete_all()
    assert not list(graph.query.all())
    graph.query.run('CREATE (p:Person {name: "Bob"})')
    all_nodes = list(graph.query('MATCH (all) RETURN all'))
    assert len(all_nodes) == 1
    assert len(all_nodes[0]) == 1
    assert all_nodes[0][0]['name'] == 'Bob'
    graph.delete_all()
    assert not list(graph.query.all())
