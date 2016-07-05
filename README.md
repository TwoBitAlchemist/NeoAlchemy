NeoAlchemy
==========

NeoAlchemy is a SqlAlchemy-like tool for working with the Neo4J graph database
in Python. It is intended to be very easy to use, and intuitively familiar to
anyone who has used SqlAlchemy and/or the Cypher Query Language.

NeoAlchemy is built on top of the Neo4J Bolt driver and only supports Neo4J
3.0+ connected over the Bolt protocol. It supports Python 2.7 and 3.3+.

Getting Started
---------------

NeoAlchemy is available on [PyPI][1], so it can be installed normally using
`pip install neoalchemy`. NeoAlchemy is built on top of the [official Neo4J
Python driver][2], and that is its only dependency. If you install from PyPI,
this will automatically be installed alongside it.

[Questions, support requests, comments][3], and [contributions][4] should be
directed to GitHub accordingly.

Low-Level QueryBuilder API
--------------------------

``` python
from neoalchemy import NodeType, Property, Graph

graph = Graph()

user = NodeType('User',  # primary label
    Property('id', unique=True, type=int),
    Property('name', indexed=True),
    Property('fullname', required=True)
)

# Emit schema-generating DDL
graph.schema.add(user)
```


High-Level Schema ORM
---------------------

``` python
from neoalchemy import Node, Property, Graph

class User(Node):
    graph = Graph()

    id = Property(unique=True, type=int)
    name = Property(indexed=True)
    fullname = Property(required=True)

# Cypher schema generation emitted automatically
# No user action required
```


[1]: https://pypi.python.org/pypi
[2]: https://neo4j.com/developer/python/
[3]: https://github.com/TwoBitAlchemist/NeoAlchemy/issues/new
[4]: https://github.com/TwoBitAlchemist/NeoAlchemy
