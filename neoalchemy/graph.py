"""
A thin wrapper around the Neo4J Bolt driver's GraphDatabase class
providing a convenient auto-connection during initialization.
"""
from collections import OrderedDict

import warnings

from neo4j.v1 import GraphDatabase, basic_auth


class QueryLog(OrderedDict):
    MAX_LOG_SIZE = 5

    def __init__(self, max_size=None, *args, **kw):
        self.__log_line = 0
        if max_size is not None:
            self.__max_size = max_size

    def __call__(self, statement):
        line = self.__log_line
        self[line] = statement
        if len(self) > self.MAX_LOG_SIZE:
            self.pop(line - self.MAX_LOG_SIZE)
        self.__log_line += 1

    def clear(self):
        self.__log_line = 0
        super().clear()

    def __iter__(self):
        return iter(self.values())

    def __setitem__(self, key, value):
        if key != self.__log_line:
            raise KeyError('%s not writeable at '
                           'line [%s].' % (self.__class__.__name__, key))
        super().__setitem__(key, value)


class Query(object):
    """Run queries on the Graph"""
    def __init__(self, graph):
        self.__graph = graph
        self.__log = QueryLog()

    def __call__(self, statement, **params):
        return self.run(statement, **params)

    @property
    def log(self):
        return self.__log

    def all(self):
        """MATCH (all) RETURN all"""
        return self.run('MATCH (all) RETURN all')

    def run(self, statement, **params):
        """Run an arbitrary Cypher statement"""
        with self.__graph.session() as session:
            self.log(statement)
            return session.run(statement, **params)


class Reflect(object):
    def __init__(self, graph):
        self.__graph = graph

    def constraints(self):
        constraints = self.__graph.query('CALL db.constraints()') or ()
        return (r['constraint'] for r in constraints)

    def indexes(self):
        indexes = self.__graph.query('CALL db.indexes()') or ()
        return (r['index'] for r in indexes)

    def labels(self):
        labels = self.__graph.query('CALL db.labels()') or ()
        return (r['label'] for r in labels)


class Schema(object):
    def __init__(self, graph):
        self.__graph = graph
        self.__constraints = None
        self.__indexes = None
        self.__labels = None
        self.__reflect = Reflect(graph)
        self.__schema = dict()

    def add(self, nodetype, overwrite=False):
        if nodetype.label in self.__schema:
            return

        self.__schema[nodetype.label] = str(nodetype)
        # Scan the graph for the schema
        if overwrite or nodetype.label not in self.labels():
            if overwrite:
                self.__graph.query(str(nodetype).replace('CREATE', 'DROP'))
            return self.__graph.query(str(nodetype))

    def constraints(self):
        if self.__constraints is None:
            self.__constraints = tuple(self.__reflect.constraints())
        return self.__constraints

    def indexes(self):
        if self.__indexes is None:
            self.__indexes = tuple(self.__reflect.indexes())
        return self.__indexes

    def labels(self):
        if self.__labels is None:
            self.__labels = tuple(self.__reflect.labels())
        return self.__labels

    @property
    def ls(self):
        return '\n'.join(filter(bool, map(str, self.__schema.values())))

    def update(self):
        self.__constraints = tuple(self.__reflect.constraints())
        self.__indexes = tuple(self.__reflect.indexes())
        self.__labels = tuple(self.__reflect.labels())


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

    def connect(self, url=None, user=None, password=None):
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
                warnings.warn('Switching protocols. Only Bolt is supported '
                              'at this time.')
        except ValueError:
            pass

        try:
            credentials, url = url.split('@')
        except ValueError:
            auth_token = basic_auth(user, password)
        else:
            auth_token = basic_auth(*credentials.split(':', 1))

        self.driver = GraphDatabase.driver('bolt://%s' % url, auth=auth_token)

    def delete_all(self):
        """MATCH (all) DETACH DELETE all"""
        with self.session() as session:
            session.run('MATCH (all) DETACH DELETE all')

    def session(self):
        return self.driver.session()
