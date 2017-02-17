"""Schema OGM tests"""
from datetime import date
import os
import uuid

import pytest

from neoalchemy import (Graph, OGMBase, Property,
                        OneToManyRelation, ManyToManyRelation)
from neoalchemy.graph import Query, Schema
from neoalchemy.validators import isodate, UUID


class FakeQuery(Query):
    def run(self, query, **params):
        self.log(query, params)


class FakeGraph(Graph):
    def __init__(self, **kw):
        super(FakeGraph, self).__init__(encrypted=False, **kw)
        self.__query = FakeQuery(self)

    @property
    def query(self):
        return self.__query


@pytest.fixture
def graph():
    if 'NEOALCHEMY_TEST_GRAPH' in os.environ:
        graph_args = {
            'user': os.environ.get('NEOALCHEMY_TEST_USER'),
            'password': os.environ.get('NEOALCHEMY_TEST_PASS'),
            'encrypted': False,
        }
        if os.environ.get('NEOALCHEMY_TEST_URL'):
            return Graph(os.environ['NEOALCHEMY_TEST_URL'], **graph_args)
        else:
            return Graph(**graph_args)
    else:
        return FakeGraph()


@pytest.fixture
def clear_graph(graph):
    if not isinstance(graph, FakeGraph):
        graph.schema.drop_all()
        graph.delete_all()
    return graph


class OGMTestClass(OGMBase):
    graph = graph()
    __abstract__ = True


class Address(OGMTestClass):
    street_level = Property()
    city = Property()


class DomesticAddress(Address):
    state = Property()
    zip_code = Property()


class InternationalAddress(Address):
    postal_code = Property()


class Customer(OGMTestClass):
    username = Property(primary_key=True)
    email = Property(primary_key=True)
    addresses = ManyToManyRelation(Address)
    orders = OneToManyRelation('PLACED_ORDER', restrict_types=('Order',),
                               backref='customer')


class Order(OGMTestClass):
    id = Property(type=UUID, default=uuid.uuid4, primary_key=True,
                  indexed=True)


graph_test = pytest.mark.skipif(os.environ.get('NEOALCHEMY_TEST_GRAPH') is None,
                                reason='No graph connection available.')
def test_make_an_order(clear_graph):
    order = Order().merge()
