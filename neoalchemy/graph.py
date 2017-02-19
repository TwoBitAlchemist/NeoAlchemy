"""
A thin wrapper around the Neo4J Bolt driver's GraphDatabase class
providing a convenient auto-connection during initialization.
"""
from collections import deque, namedtuple
import warnings

from neo4j.v1 import (GraphDatabase, basic_auth, Record,
                      Node as NeoNode, Relationship as NeoRelationship)

from .primitives import Node, Relationship


class Rehydrator(object):
    def __init__(self, statement_result, graph):
        self.__result_set = iter(statement_result)
        self.__schema = dict(graph.schema.classes)

    def __iter__(self):
        return self

    def __next__(self):
        record = next(self.__result_set)
        values = []
        for value in record.values():
            if isinstance(value, NeoNode):
                try:
                    cls = self.__schema[tuple(value.labels)]
                except KeyError:
                    values.append(Node(*value.labels, **value.properties))
                else:
                    values.append(cls(**value.properties))
            elif isinstance(value, NeoRelationship):
                values.append(Relationship(value.type, **value.properties))
            else:
                values.append(value)
        return Record(record.keys(), values)

    def next(self):
        return self.__next__()

    @property
    def one(self):
        try:
            record = next(self)
        except StopIteration:
            return None
        else:
            try:
                next(self)
            except StopIteration:
                pass
            else:
                warnings.warn('More than one result returned. Data discarded!')

        if len(record.keys()) > 1:
            return record
        else:
            return record[0]


class QueryLog(deque):
    MAX_SIZE = 100
    LogLine = namedtuple('LogLine', ('query', 'params'))

    def __init__(self, *args, **kw):
        super(QueryLog, self).__init__(maxlen=self.MAX_SIZE, *args, **kw)

    def __call__(self, query, params):
        self.append(self.LogLine(query=query, params=params))


class Query(object):
    """Run queries on the Graph"""
    def __init__(self, graph):
        self.__graph = graph
        self.__log = QueryLog()

    def __call__(self, q, **params):
        """Syntactic sugar for query.run(str(q), **params)"""
        return self.run(str(q), **params)

    @property
    def log(self):
        return self.__log

    def all(self):
        """MATCH (all) RETURN all"""
        return self.run('MATCH (all) RETURN all')

    def run(self, query, **params):
        """Run an arbitrary Cypher query"""
        with self.__graph.session() as session:
            self.log(query, params)
            return session.run(query, parameters=params)


class Reflect(object):
    def __init__(self, graph):
        self.__graph = graph

    def constraints(self):
        """Fetch the current graph constraints"""
        constraints = self.__graph.query('CALL db.constraints()') or ()
        return (r['description'] for r in constraints)

    def indexes(self):
        """Fetch the current graph indexes"""
        indexes = self.__graph.query('CALL db.indexes()') or ()
        return (r['description'] for r in indexes)

    def labels(self):
        """Fetch the current graph labels"""
        labels = self.__graph.query('CALL db.labels()') or ()
        return (r['label'] for r in labels)


class Schema(object):
    def __init__(self, graph):
        self.__graph = graph
        self.__constraints = None
        self.__indexes = None
        self.__labels = None
        self.__reflect = Reflect(graph)
        self.__schema = set()
        self.__hierarchy = dict()
        self.__relations = dict()

    def add(self, obj):
        """
        Add the object's schema, if not already present.
        """
        node = obj.__node__
        if not node.type or node.type in self.__schema:
            return

        def get_or_defer(type_):
            try:
                type_ = self.__hierarchy[type_]
            except KeyError:
                if type_ not in self.__hierarchy.values():
                    deferred = self.__relations.setdefault(type_, [])
                    deferred.append(rel)
                    return
            return type_

        self.__schema.add(node.type)
        if obj.__node__ is not obj:
            self.__hierarchy[node.labels] = obj
            if node.type:
                self.__hierarchy[node.type] = obj

            # add backrefs to deferred types
            deferred_types = list(self.__relations.keys())
            for type_ in deferred_types:
                type_class = get_or_defer(type_)
                if type_class is not None:
                    for rel in self.__relations[type_]:
                        rel.create_backref(type_class)

            # add backrefs to new types, or defer them
            for attr in obj.__relations__:
                rel = getattr(obj, attr)
                for type_ in rel.restricted_types:
                    type_ = get_or_defer(type_)
                    if type_ is not None:
                        rel.create_backref(type_)

        schema = self.indexes() + self.constraints()
        for index_or_constraint in node.schema:
            if index_or_constraint not in schema:
                self.__graph.query('CREATE ' + index_or_constraint)

    def drop(self, obj):
        """
        Drop the object's schema, if present.
        """
        node = obj.__node__
        if node.type in self.__schema:
            self.__schema.remove(node.type)

        schema = self.indexes() + self.constraints()
        for index_or_constraint in node.schema:
            if index_or_constraint in schema:
                self.__graph.query('DROP ' + index_or_constraint)

    def drop_all(self):
        for constraint in self.constraints():
            self.__graph.query('DROP ' + constraint)
        for index in self.__reflect.indexes():
            self.__graph.query('DROP ' + index)

    @property
    def classes(self):
        return self.__hierarchy.items()

    def constraints(self):
        """
        Get current graph constraints lazily.

        On first access, this fetches from the database. Afterwards, call
        update() to refresh.
        """
        if self.__constraints is None:
            self.__constraints = tuple(self.__reflect.constraints())
        return self.__constraints

    def indexes(self):
        """
        Get current graph indexes lazily.

        On first access, this fetches from the database. Afterwards, call
        update() to refresh.
        """
        if self.__indexes is None:
            self.__indexes = tuple(self.__reflect.indexes())
        return self.__indexes

    def labels(self):
        """
        Get current graph labels lazily.

        On first access, this fetches from the database. Afterwards, call
        update() to refresh.
        """
        if self.__labels is None:
            self.__labels = tuple(self.__reflect.labels())
        return self.__labels

    @property
    def ls(self):
        """Cypher statements for currently defined schema"""
        return '\n'.join(self.indexes() + self.constraints())

    def update(self):
        """Refresh graph constraints, indexes, and labels"""
        self.__constraints = tuple(self.__reflect.constraints())
        self.__indexes = tuple(self.__reflect.indexes())
        self.__labels = tuple(self.__reflect.labels())
        return self


class Graph(GraphDatabase):
    """
    A thin wrapper around the Neo4J Bolt driver's GraphDatabase class
    providing a convenient auto-connection during initialization.
    """
    def __init__(self, url=None, **kw):
        self.connect(url, **kw)
        self.__query = Query(self)
        self.__schema = Schema(self)

    @property
    def query(self):
        return self.__query

    @property
    def schema(self):
        return self.__schema

    def connect(self, url=None, user=None, password=None, **kw):
        """
        Parse a Neo4J URL and attempt to connect using Bolt

        Note: If the user and password arguments are provided, they
        will only be used in case no auth information is provided as
        part of the connection URL.
        """
        if url is None:
            url = 'bolt://localhost'
        if user is None:
            user = 'neo4j'
        if password is None:
            password = 'neo4j'

        try:
            protocol, url = url.split('://')
            if protocol.lower() != 'bolt':
                warnings.warn('Switching protocols. Only Bolt is supported.')
        except ValueError:
            pass

        try:
            credentials, url = url.split('@')
        except ValueError:
            kw['auth'] = basic_auth(user, password)
        else:
            kw['auth'] = basic_auth(*credentials.split(':', 1))

        self.driver = GraphDatabase.driver('bolt://%s' % url, **kw)

    def delete_all(self):
        """MATCH (all) DETACH DELETE all"""
        with self.session() as session:
            session.run('MATCH (all) DETACH DELETE all')

    def session(self):
        """Syntactic sugar for graph.driver.session()"""
        return self.driver.session()
