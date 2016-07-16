"""
A thin wrapper around the Neo4J Bolt driver's GraphDatabase class
providing a convenient auto-connection during initialization.
"""
from collections import deque, namedtuple
import warnings

from neo4j.v1 import GraphDatabase, basic_auth


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

    def add(self, nodetype):
        """
        Add a NodeType to the schema, if not already present.
        """
        if nodetype.LABEL in self.__schema:
            return

        self.__schema.add(nodetype.LABEL)
        schema = self.indexes() + self.constraints()

        for index_or_constraint in nodetype.schema:
            if index_or_constraint not in schema:
                self.__graph.query('CREATE ' + index_or_constraint)

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
                warnings.warn('Switching protocols. Only Bolt is supported.')
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
        """Syntactic sugar for graph.driver.session()"""
        return self.driver.session()
