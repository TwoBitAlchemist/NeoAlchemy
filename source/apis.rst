

Getting to Know NeoAlchemy
==========================

.. note::
    Got a graph full of data already? Don't worry! NeoAlchemy fully supports
    reflecting your database. If you're just starting out with NeoAlchemy, it
    is still recommended that you skim this section as an introduction to its
    capabilities.


NeoAlchemy features both a low-level and a high-level API for working with
Neo4J. The low-level API aims to be **expressive**, offering the user
**flexibility** and **control**. Using the low-level API can feel somewhat
like writing Cypher, and the framework tries to stay out of your way as much as
possible. The high-level API is built on top of the low-level API, and trades
control for **automation**. Using the high-level API, you can lay out your
graph schema using a hierarchy of normal Python classes. These classes offer
convenient methods for interacting with the graph without having to manually
write queries.

.. note::
    You don't have to choose between APIs! The low-level and high-level APIs
    can be used in conjunction with one another as well as with manual Cypher
    querying through the Graph object.


The Lower-Level API
-------------------

The lower-level NeoAlchemy API is somewhat akin to the `SqlAlchemy Expression
Language`_. Just like with SqlAlchemy, we start by defining our schema and
creating the appropriate metadata::

    from sqlalchemy import Table, Column, Integer, String, MetaData

    metadata = MetaData()

    users = Table('users', metadata,
        Column('id', Integer, primary_key=True),
        Column('name', String),
        Column('fullname', String)
    )

    # Emit schema-generating DDL
    metadata.create_all(engine)


This defines a simple ``users`` table with three columns -- an ``id``, a 
``name``, and ``fullname``. A call to ``metadata.create_all()`` is required to
emit schema-generating DDL, laying out the empty table.

The same thing in NeoAlchemy looks like this::

    from neoalchemy import NodeType, Property, Graph

    graph = Graph()

    user = NodeType('User',  # primary label
        Property('id', unique=True, type=int),
        Property('name', indexed=True)
        Property('fullname', required=True)
    )

    # Emit schema-generating DDL
    graph.schema.add(user)


This creates a simple ``NodeType`` with three properties similar to the above
table. Each property represents an available `constraint`_ in Neo4J. The
proper indexes and constraints are created when ``graph.schema.add`` is called.

.. note::
    The ``required`` property represents a `Property Existence constraint`_
    which is only supported in the `Neo4J Enterprise Edition`_.


The Higher-Level API
-------------------

The higher-level API is like `SqlAlchemy's Declarative ORM`_. Python classes
are used to map metadata to the database transparently::

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
to manually trigger metadata creation. Since every class is connected to a
graph explicitly via its ``.graph`` property, users running multiple instances
of Neo4J should have no trouble distinguishing which classes map to which
graphs, even if multiple classes touching different graphs are grouped in the
same file.


.. _SqlAlchemy Expression Language: http://docs.sqlalchemy.org/en/latest/core/tutorial.html
.. _constraint: https://neo4j.com/docs/developer-manual/current/#query-constraints
.. _Property Existence constraint: https://neo4j.com/docs/developer-manual/current/#constraints-create-node-property-existence-constraint
.. _Neo4J Enterprise Edition: https://neo4j.com/editions/
.. _SqlAlchemy's Declarative ORM: http://docs.sqlalchemy.org/en/latest/orm/tutorial.html
