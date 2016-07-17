NeoAlchemy
==========

[![Documentation Status](https://readthedocs.org/projects/neoalchemy/badge/?version=latest)](http://neoalchemy.readthedocs.io/en/latest/?badge=latest)
[![Build Status](https://travis-ci.org/TwoBitAlchemist/NeoAlchemy.svg?branch=master)](https://travis-ci.org/TwoBitAlchemist/NeoAlchemy)
[![codecov](https://codecov.io/gh/TwoBitAlchemist/NeoAlchemy/branch/master/graph/badge.svg)](https://codecov.io/gh/TwoBitAlchemist/NeoAlchemy)

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
```

[Learn more about the QueryBuilder API][5].


High-Level Schema ORM
---------------------

``` python
from neoalchemy import Node, Property, Graph

class User(Node):
    graph = Graph()

    uuid = Property(unique=True, type=valid_uuid, default=uuid.uuid4),
    real_name = Property(indexed=True),
    screen_name = Property(indexed=True, type=str.lower),
    age = Property(type=int)

# Cypher schema generation emitted automatically
# No user action required
```


[1]: https://pypi.python.org/pypi
[2]: https://neo4j.com/developer/python/
[3]: https://github.com/TwoBitAlchemist/NeoAlchemy/issues/new
[4]: https://github.com/TwoBitAlchemist/NeoAlchemy
[5]: http://neoalchemy.readthedocs.io/en/latest/query-builder.html
