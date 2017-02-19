import os
import pytest

from neoalchemy import Graph, OGMBase
from neoalchemy.graph import Query, Schema


class FakeQuery(Query):
    def run(self, query, **params):
        self.log(query, params)
        return ()


class FakeQueryContextManager(object):
    def __init__(self, fake_query):
        self.__query = fake_query

    def __enter__(self):
        return self.__query

    def __exit__(self, *args):
        pass


class FakeSchema(Schema):
    def drop_all(self):
        pass


class FakeGraph(Graph):
    def __init__(self, **kw):
        kw['encrypted'] = False
        self.__connected = False
        if 'NEOALCHEMY_TEST_GRAPH' in os.environ:
            kw.update({
                'user': os.environ.get('NEOALCHEMY_TEST_USER'),
                'password': os.environ.get('NEOALCHEMY_TEST_PASS'),
                'url': os.environ.get('NEOALCHEMY_TEST_URL'),
            })
            self.__connected = True
        super(FakeGraph, self).__init__(**kw)
        self.__query = FakeQuery(self)
        self.__schema = FakeSchema(self)

    @property
    def query(self):
        if self.__connected:
            return super(FakeGraph, self).query
        return self.__query

    @property
    def schema(self):
        if self.__connected:
            return super(FakeGraph, self).schema
        return self.__schema

    def session(self):
        if self.__connected:
            return super(FakeGraph, self).session()
        return FakeQueryContextManager(self.__query)


class OGMTestClass(OGMBase):
    graph = FakeGraph()
    __abstract__ = True
