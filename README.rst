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

    from neoalchemy import Create, Node, Property, Graph
    from neoalchemy.validators import UUID

    graph = Graph()

    person = Node('Person',  # primary label
        uuid=Property(unique=True, type=UUID, default=uuid.uuid4),
        real_name=Property(indexed=True),
        screen_name=Property(indexed=True, type=str.lower),
        age=Property(type=int)
    )

    # Emit schema-generating DDL
    graph.schema.create(person)

    person.real_name = 'Alison'
    person.screen_name = 'Ali42'
    person.age = 29
    create = Create(person)

    graph.query(create, **create.params)

`Learn more about the QueryBuilder API`_.


=====================
High-Level Schema OGM
=====================

::

    import uuid

    from neoalchemy import OGMBase, Property, Graph
    from neoalchemy.validators import UUID

    class Person(OGMBase):
        graph = Graph()

        uuid = Property(unique=True, type=UUID, default=uuid.uuid4)
        real_name = Property(indexed=True)
        screen_name = Property(indexed=True, type=str.lower)
        age = Property(type=int)

    # Cypher schema generation emitted automatically
    # No user action required

    Person(real_name='Alison', screen_name='Ali42', age=29).create()

`Learn more about the Schema OGM`_.

.. _PyPI: https://pypi.python.org/pypi/neoalchemy
.. _official Neo4J Python driver: https://neo4j.com/developer/python/
.. _Questions, support requests, comments: https://github.com/TwoBitAlchemist/NeoAlchemy/issues/new
.. _contributions: https://github.com/TwoBitAlchemist/NeoAlchemy
.. _Learn more about the QueryBuilder API: http://neoalchemy.readthedocs.io/en/0.8.0b/query-builder.html
.. _Learn more about the Schema ORM: http://neoalchemy.readthedocs.io/en/0.8.0b/schema-ORM.html
