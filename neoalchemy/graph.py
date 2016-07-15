"""
A thin wrapper around the Neo4J Bolt driver's GraphDatabase class
providing a convenient auto-connection during initialization.
"""
from collections import namedtuple, OrderedDict
import warnings

from neo4j.v1 import GraphDatabase, basic_auth


class QueryLog(OrderedDict):
    MAX_LOG_SIZE = 100

    def __init__(self, max_size=None, *args, **kw):
        self.__log_line = 0
        if max_size is not None:
            self.__max_size = max_size
        super(QueryLog, self).__init__(*args, **kw)

    def __call__(self, query, params):
        line = self.__log_line
        LogLine = namedtuple('LogLine', ('query', 'params'))
        self[line] = LogLine(query=query, params=params)
        if len(self) > self.MAX_LOG_SIZE:
            self.pop(line - self.MAX_LOG_SIZE)
        self.__log_line += 1

    def clear(self):
        self.__log_line = 0
        super(QueryLog, self).clear()

    def __iter__(self):
        return iter(self.values())

    def __setitem__(self, key, value):
        if key != self.__log_line:
            raise KeyError('%s not writeable at '
                           'line [%s].' % (self.__class__.__name__, key))
        super(QueryLog, self).__setitem__(key, value)


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

    def add(self, nodetype, overwrite=False):
        """
        Add a NodeType to the schema.

        If nodetype is already in the schema, does nothing.
        If nodetype is not in the schema, and not in the database, the
            appropriate schema-creating statements will be emitted.
        If nodetype is not in the schema, but is in the database, the schema
            will only be written if overwrite is set, in which case the
            existing schema (if any) will be dropped.
        """
        if nodetype.LABEL in self.__schema:
            return

        statement = str(nodetype)
        self.__schema.add(nodetype.LABEL)
        not_found = (statement.replace('CREATE ', '')
                     not in self.indexes() + self.constraints())
        if overwrite:
            statement = '\n'.join((statement.replace('CREATE', 'DROP'),
                                   statement))
        if overwrite or not_found:
            self.__graph.query(statement)

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
