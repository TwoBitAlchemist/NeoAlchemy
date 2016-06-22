NeoAlchemy
==========

Contents:

.. toctree::
   :maxdepth: 2


Introduction
============

As its name implies, NeoAlchemy is a SqlAlchemy-like tool for working with the
Neo4J graph database in Python. It is intended to be very easy to use, and
intuitively familiar to anyone who has used SqlAlchemy and/or the Cypher
Query Language. NeoAlchemy is built on top of the Neo4J Bolt driver and
currently only supports Neo4J 3.0+ connected over the Bolt protocol. It
supports Python 2.7 and 3.3+.


Getting Started
===============

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

    users = NodeType('User',  # primary label
        Property('id', unique=True, type=int),
        Property('name', indexed=True, type=str),
        Property('fullname', required=True, type=str)
    )

    # Emit schema-generating DDL
    graph.schema.add(users)


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

    class User(metaclass=Node):  # Python 3 only
        # __metaclass__ = Node   # Python 2 only
        graph = Graph()

        id = Property(unique=True, type=int)
        name = Property(indexed=True, type=str)
        fullname = Property(required=True, type=str)

    # Cypher schema generation emitted automatically
    # No user action required


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

