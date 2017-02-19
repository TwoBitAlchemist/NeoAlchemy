"""Schema OGM tests"""
import os

import pytest

from neoalchemy import Graph
from MockProject.customers import Customer
from MockProject.graph import FakeGraph
from MockProject.orders import Order


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
def test_a_customer_places_an_order(clear_graph):
    customer = Customer(username='seregon', email='seregon@gmail.com').merge()
    assert isinstance(customer, Customer)
    assert customer.username == 'seregon'
    assert customer.email == 'seregon@gmail.com'
    order = Order().merge()
    assert isinstance(order, Order)
    assert order.id is not None
    customer.orders.add(order)
