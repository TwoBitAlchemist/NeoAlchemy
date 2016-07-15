"""Graph (Connection Class) Tests"""
import os

import pytest

from neoalchemy import Graph


__TEST_LABEL__ = '__NEOALCHEMY_TEST__'


TEST_NEO_URL = os.environ.get('TEST_NEOALCHEMY_URL', None)
TEST_NEO_USER = os.environ.get('TEST_NEOALCHEMY_USER', None)
TEST_NEO_PASS = os.environ.get('TEST_NEOALCHEMY_PASS', None)
CAN_CLEAR_GRAPH = bool(os.environ.get('TEST_NEOALCHEMY_GRAPH_FULL_ACCESS', 0))
CAN_WRITE_GRAPH = (CAN_CLEAR_GRAPH or
                   bool(os.environ.get('TEST_NEOALCHEMY_GRAPH_ACCESS', 0)))


GRAPH_CLEARS_DISABLED_MSG = ("Graph clearing disabled. Enable with "
                             "`export TEST_NEOALCHEMY_GRAPH_FULL_ACCESS=1`\n"
                             "WARNING: THIS WILL DELETE YOUR ENTIRE GRAPH!!!")
GRAPH_WRITES_DISABLED_MSG = ("Graph writes disabled. Enable with "
                             "`export TEST_NEOALCHEMY_GRAPH_ACCESS=1`")

clears_graph = pytest.mark.skipif(not CAN_CLEAR_GRAPH,
                                  reason=GRAPH_CLEARS_DISABLED_MSG)
writes_required = pytest.mark.skipif(not CAN_WRITE_GRAPH,
                                     reason=GRAPH_WRITES_DISABLED_MSG)


test_graph = Graph(TEST_NEO_URL, user=TEST_NEO_USER, password=TEST_NEO_PASS)


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
