

**************************
Getting to Know NeoAlchemy
**************************

NeoAlchemy features both a low-level and a high-level API for working with
Neo4J. The low-level API aims to be **expressive**, offering the user
**flexibility** and **control**.  The high-level API is built on top of the
low-level API, and trades control for **automation**.

You don't have to choose between APIs! The low-level and high-level APIs can be
used in conjunction with one another as well as with manual Cypher querying
with :py:class:`graph.query`.


=================
The Low-Level API
=================

NeoAlchemy's low-level API is called QueryBuilder. It is similar in feel and
purpose to the `SqlAlchemy Expression Language`_. In SqlAlchemy, defining
the schema for a table and writing its metadata to the database looks like
this::

    from sqlalchemy import Table, Column, Integer, String, MetaData

    metadata = MetaData()

    users = Table('users', metadata,
        Column('id', Integer, primary_key=True),
        Column('name', String),
        Column('fullname', String)
    )

    # Emit schema-generating DDL
    metadata.create_all(engine)


This defines a simple :py:data:`users` table with three columns.  A call to
:py:meth:`metadata.create_all()` is required to emit schema-generating DDL,
laying out the empty table.

The same thing in NeoAlchemy looks like this::

    from neoalchemy import NodeType, Property, Graph

    graph = Graph()

    user = NodeType('User',  # primary label
        Property('id', unique=True, type=int),
        Property('name', indexed=True),
        Property('fullname', required=True)
    )

    # Emit schema-generating DDL
    graph.schema.add(user)


This creates a simple :py:class:`NodeType` with three properties similar to the
above table. Each property represents an available `constraint`_ in Neo4J. The
proper indexes and constraints are created when :py:meth:`graph.schema.add` is
called.

.. note::
    The ``required`` property represents a `Property Existence constraint`_
    which is only supported in the `Neo4J Enterprise Edition`_.

Can't wait to learn more? Dive into :doc:`query-builder`.


==================
The High-Level API
==================

NeoAlchemy's high-level API is the Schema ORM. Python classes are used to
map metadata to the database transparently. It is compared below to
`SqlAlchemy's Declarative ORM`_::

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


The same thing in NeoAlchemy looks like this::

    from neoalchemy import Node, Property, Graph

    class User(Node):
        graph = Graph()

        id = Property(unique=True, type=int)
        name = Property(indexed=True)
        fullname = Property(required=True)

    # Cypher schema generation emitted automatically
    # No user action required

Notice that unlike SqlAlchemy, we have far less to import and we do not need
to manually trigger metadata creation. We also don't have to explicitly
specify a primary label for our underlying :py:class:`NodeType`. NeoAlchemy
uses the name of the class if none is specified.

.. note::
    Since every class is connected to a graph explicitly via its ``.graph``
    property, users running multiple instances of Neo4J should have no trouble
    distinguishing which classes map to which graphs, even if multiple classes
    touching different graphs are grouped in the same file.

Wanna learn more? Skip straight to the :doc:`schema-ORM`.

.. _SqlAlchemy Expression Language: http://docs.sqlalchemy.org/en/latest/core/tutorial.html
.. _constraint: https://neo4j.com/docs/developer-manual/current/#query-constraints
.. _Property Existence constraint: https://neo4j.com/docs/developer-manual/current/#constraints-create-node-property-existence-constraint
.. _Neo4J Enterprise Edition: https://neo4j.com/editions/
.. _SqlAlchemy's Declarative ORM: http://docs.sqlalchemy.org/en/latest/orm/tutorial.html
