

***************
Getting Started
***************

============
Installation
============

NeoAlchemy is available on `PyPI`_, so it can be installed normally using ``pip
install neoalchemy``. NeoAlchemy is built on top of the `official Neo4J Python
driver`_. If you install from PyPI, this will automatically be installed
alongside it. You can also install the dependencies using ``pip install -r
requirements.txt``.

`Questions, support requests, comments`_, and `contributions`_ should be
directed to GitHub accordingly.


=====================
Connecting to a Graph
=====================

Connecting to a graph is designed to be as easy and painless as possible. In
general, you only have to specify what you have changed from the default
Neo4J settings, and NeoAlchemy will infer the rest.

For example, if you connect to your graph with the username and password
``neo4j`` at the default port (7687) on ``localhost``, connecting to a graph is
as simple as::

    from neoalchemy import Graph

    graph = Graph()


On the other hand, if you'd changed your Neo4J password to ``password``, you
could connect like this::

    graph = Graph(password='password')

Of course, you can have a completely custom setup if you like. Just pass a URL
and :py:class:`Graph` will parse it for you::

    graph = Graph('bolt://my_user:my_pass@my.neo4j.server.com:24789')

You can also pass the username and password in separately if you like::

    graph = Graph('bolt://my.neo4j.server.com:24789',
                  user='my_user', password='password')

.. note::
    NeoAlchemy only supports connecting over `the Bolt protocol`_. This also
    means that only Neo4J version 3.0 or higher is supported.


.. _PyPI: https://pypi.python.org/pypi
.. _official Neo4J Python driver: https://neo4j.com/developer/python/
.. _Questions, support requests, comments: https://github.com/TwoBitAlchemist/NeoAlchemy/issues/new
.. _contributions: https://github.com/TwoBitAlchemist/NeoAlchemy
.. _the Bolt protocol: https://neo4j.com/blog/neo4j-3-0-milestone-1-release/
