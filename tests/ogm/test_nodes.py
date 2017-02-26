"""Schema OGM tests"""
import os

import pytest

from neoalchemy import Graph
from MockProject.customers import Customer
from MockProject.graph import FakeGraph
from MockProject.orders import Order, OrderItem


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
    order_id = order.id
    assert isinstance(order, Order)
    assert order.id is not None
    customer.orders.add(order)
    assert len(list(customer.orders.match())) == 1
    customer = Customer.match(email='seregon@gmail.com').one
    assert isinstance(customer, Customer)
    assert customer.username == 'seregon'
    assert customer.email == 'seregon@gmail.com'
    assert len(list(customer.orders.match())) == 1
    order = customer.orders.match().one
    assert isinstance(order, Order)
    assert order.id == order_id
    assert order.customer.email == 'seregon@gmail.com'
    item = OrderItem(line_item='bread', price='2.00').create()
    other_item = OrderItem(line_item='milk', price='3.00').create()
    order.items.add(item)
    order.items.add(other_item)
    assert len(list(order.items.match())) == 2
