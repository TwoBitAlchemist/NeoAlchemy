NeoAlchemy
==========

NeoAlchemy is a SqlAlchemy-like tool for working with the Neo4J graph database
in Python. It is intended to be very easy to use, and intuitively familiar to
anyone who has used SqlAlchemy and/or the Cypher Query Language.

NeoAlchemy is built on top of the Neo4J Bolt driver and currently only supports
Neo4J 3.0+ connected over the Bolt protocol. It supports Python 2.7 and 3.3+.

Getting Started
---------------

NeoAlchemy is available on `PyPI`_, so it can be installed normally using ``pip
install neoalchemy``. NeoAlchemy is built on top of the `official Neo4J Python
driver`_, and that is its only dependency. If you install from PyPI, this will
automatically be installed alongside it.

`Questions, support requests, comments`_, and `contributions`_ should be
directed to GitHub accordingly.


Connecting to a Graph
---------------------

Connecting to a graph is designed to be easy and as painless as possible. In
general, you only have to specify what you have changed from the default
Neo4J settings, and NeoAlchemy will infer the rest.

For example, if you connect to your graph with the username and password
``neo4j`` at the default port (7474) on ``localhost``, connecting to a graph is
as simple as::

    from neoalchemy import Graph

    graph = Graph()


On the other hand, if you'd changed your Neo4J password to ``password``, you
could connect like this::

    graph = Graph(password='password')

Of course, you can have a completely custom setup if you like. Just pass a URL
and the Graph class will parse it for you::

    graph = Graph('bolt://my_user:my_pass@my.neo4j.server.com:24789')

You can also pass the username and password in separately if you like::

    graph = Graph('bolt://my.neo4j.server.com:24789',
                  user='my_user', password='password')
