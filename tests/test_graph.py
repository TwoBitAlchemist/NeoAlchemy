"""Graph (Connection Class) Tests"""
import pytest

from neoalchemy import Graph


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


def test_separate_user_pass():
    graph = Graph('bolt://localhost:7474', user='user', password='pass')
    assert graph.driver.url == 'bolt://localhost:7474'
    assert graph.driver.host == 'localhost'
    assert graph.driver.port == 7474
    assert graph.driver.config['auth'].scheme == 'basic'
    assert graph.driver.config['auth'].principal == 'user'
    assert graph.driver.config['auth'].credentials == 'pass'
