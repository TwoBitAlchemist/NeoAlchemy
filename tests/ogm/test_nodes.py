"""Schema OGM tests"""
import os

import pytest

from neoalchemy import Graph
from tests.ogm.MockProject.graph import FakeGraph
from tests.ogm.MockProject.orders import Order


graph_test = pytest.mark.skipif(os.environ.get('NEOALCHEMY_TEST_GRAPH') is None,
                                reason='No graph connection available.')


@pytest.fixture
def graph():
    return FakeGraph()


@pytest.fixture
def clear_graph(graph):
    graph.schema.drop_all()
    graph.delete_all()
    return graph


@graph_test
def test_make_an_order(clear_graph):
    order = Order().merge()
