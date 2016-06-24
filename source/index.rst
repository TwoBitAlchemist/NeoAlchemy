NeoAlchemy
==========

Contents:

.. toctree::
   :maxdepth: 2

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`



Introduction
============

As its name implies, NeoAlchemy is a SqlAlchemy-like tool for working with the
Neo4J graph database in Python. It is intended to be very easy to use, and
intuitively familiar to anyone who has used SqlAlchemy and/or the Cypher
Query Language.

NeoAlchemy is built on top of the Neo4J Bolt driver and
currently only supports Neo4J 3.0+ connected over the Bolt protocol. It
supports Python 2.7 and 3.3+.


Getting Started
===============

Creating a Schema
-----------------

SqlAlchemy Expression Language::

    from sqlalchemy import Table, Column, Integer, String, MetaData

    metadata = MetaData()

    users = Table('users', metadata,
        Column('id', Integer, primary_key=True),
        Column('name', String),
        Column('fullname', String)
    )

    # Emit schema-generating DDL
    metadata.create_all(engine)


The same thing in NeoAlchemy::

    from neoalchemy import NodeType, Property, Graph

    graph = Graph()

    user = NodeType('User',  # primary label
        Property('id', unique=True, type=int),
        Property('name', indexed=True)
        Property('fullname', required=True)
    )

    # Emit schema-generating DDL
    graph.schema.add(user)


Or using SqlAlchemy's Declarative ORM::

    from sqlalchemy import Column, Integer, String
    from sqlalchemy.ext.declarative import declarative_base

    Base = declarative_base()

    class User(Base):
        __tablename__ = 'users'

        id = Column(Integer, primary_key=True)
        name = Column(String)
        fullname = Column(String)

    # Emit schema-generating DDL
    Base.metadata.create_all(engine)


The same thing in NeoAlchemy::

    from neoalchemy import Node, Property, Graph

    class User(Node):
        graph = Graph()

        id = Property(unique=True, type=int)
        name = Property(indexed=True)
        fullname = Property(required=True)

    # Cypher schema generation emitted automatically
    # No user action required


Creating Nodes and Relationships
--------------------------------

Like SqlAlchemy, NeoAlchemy features a low-level and a high-level database
API. The lower-level API offers **control** and **flexibility**, while the
higher-level API offers **automation**. You can use either or both, however
you choose. The two APIs do not conflict in any way. The high-level API is
built on top of the low-level API, and in many places is syntactic sugar.


The low-level API is a query-building API, and aims to feel like writing
Cypher in Python. The ``Create`` object works with the low-level ``NodeType``
class to automate producing parametrized Cypher queries ready for
consumption by a call to ``graph.query``.

Let's start with a simplified version of ``user`` from above::

    In [1]: user = NodeType('User', Property('name', unique=True))

Then import ``Create``::

    In [2]: from neoalchemy.cypher import Create

    In [3]: create = Create(users)

This gives you a ``Create`` object, a simple query builder. You can stringify
it to see the underlying Cypher statement::

    In [4]: str(create)
    Out[4]: 'CREATE (node:User {name: {name}})'

The query expects a parameter to correspond with the ``Property`` we defined.
You can see the current dict of parameters::

    In [5]: create.params
    Out[5]: {'name': None}

Once you set it::

    In [6]: create.params['name'] = 'Neo'

It's ready to be written to the graph::

    In [7]: graph.query(create, **create.params)
    Out[7]: <neo4j.v1.session.StatementResult at 0x7ffa9e73d470>

Like Cypher, NeoAlchemy endeavors to allow you to express nodes and 
relationships **visually**, using an ASCII-art-like syntax::

    In [8]: create = Create(user)['KNOWS'](user)

    In [9]: str(create)
    Out[9]: 'CREATE (node:User {name: {name}})-[:KNOWS]->(node1:User {name1: {name1}})'

As you can see, this builds a query that creates a simple relationship between
two users. As before, it needs values set for its parameters::

    In [10]: create.params
    Out[10]: {'name': None, 'name1': None}

but is otherwise ready for ``graph.query``.
