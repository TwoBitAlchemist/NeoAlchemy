**********
NeoAlchemy
**********

.. image:: https://readthedocs.org/projects/neoalchemy/badge/?version=0.8.0b
    :target: http://neoalchemy.readthedocs.io/en/latest/?badge=0.8.0b
    :alt: Docs for 0.8.0b
.. image:: https://travis-ci.org/TwoBitAlchemist/NeoAlchemy.svg?branch=v0.8.0b
    :target: https://travis-ci.org/TwoBitAlchemist/NeoAlchemy

.. image:: https://codecov.io/gh/TwoBitAlchemist/NeoAlchemy/branch/0.8.0b/graph/badge.svg
    :target: https://codecov.io/gh/TwoBitAlchemist/NeoAlchemy

NeoAlchemy is a SqlAlchemy-like tool for working with the Neo4J graph database
in Python. It is intended to be very easy to use, and intuitively familiar to
anyone who has used SqlAlchemy and/or the Cypher Query Language.

NeoAlchemy is built on top of the Neo4J Bolt driver and only supports Neo4J
3.0+ connected over the Bolt protocol. It supports Python 2.7 and 3.3+.

===============
Getting Started
===============

NeoAlchemy is available on `PyPI`_, so it can be installed normally using
`pip install neoalchemy`. NeoAlchemy is built on top of the `official Neo4J
Python driver`_. If you install from PyPI, this will automatically be
installed alongside it. You can also install the dependencies using `pip
install -r requirements.txt`.

`Questions, support requests, comments`_, and `contributions`_ should be
directed to GitHub accordingly.

==========================
Low-Level QueryBuilder API
==========================

::

    import uuid

    from neoalchemy import NodeType, Property, Graph
    from neoalchemy.cypher import Create
    from neoalchemy.types import valid_uuid

    graph = Graph()

    Person = NodeType('Person',  # primary label
        Property('uuid', unique=True, type=valid_uuid, default=uuid.uuid4),
        Property('real_name', indexed=True),
        Property('screen_name', indexed=True, type=str.lower),
        Property('age', type=int)
    )

    # Emit schema-generating DDL
    graph.schema.add(Person)

    create = Create(Person).set(real_name='Alison', screen_name='Ali42')
    create.set(age=29).compile()

    graph.query(create, **create.params)

`Learn more about the QueryBuilder API`_.


=====================
High-Level Schema ORM
=====================

::

    import uuid

    from neoalchemy import Node, Property, Graph
    from neoalchemy.types import valid_uuid

    class Person(Node):
        graph = Graph()

        uuid = Property(unique=True, type=valid_uuid, default=uuid.uuid4)
        real_name = Property(indexed=True)
        screen_name = Property(indexed=True, type=str.lower)
        age = Property(type=int)

    # Cypher schema generation emitted automatically
    # No user action required

`Learn more about the Schema ORM`_.

.. _PyPI: https://pypi.python.org/pypi/neoalchemy
.. _official Neo4J Python driver: https://neo4j.com/developer/python/
.. _Questions, support requests, comments: https://github.com/TwoBitAlchemist/NeoAlchemy/issues/new
.. _contributions: https://github.com/TwoBitAlchemist/NeoAlchemy
.. _Learn more about the QueryBuilder API: http://neoalchemy.readthedocs.io/en/0.8.0b/query-builder.html
.. _Learn more about the Schema ORM: http://neoalchemy.readthedocs.io/en/0.8.0b/schema-ORM.html
