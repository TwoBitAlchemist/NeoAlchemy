

**************
RoadMap to 1.0
**************

======
0.8.0b
======

  - First Public Release


===
0.9
===

  - QueryBuilder :py:class:`~neoalchemy.cypher.Merge` support for
    ``ON CREATE``, ``ON MATCH``
  - :py:meth:`neoalchemy.Node.match` / :py:meth:`neoalchemy.Node.merge`
  - Schema ORM Basic Relation support
  - Smarter queries


===
1.0
===

  - Arbitrary Relationship Depth support in Schema ORM
  - Hydrate: ``neo4j.v1.StatementResult`` => Schema ORM class
    (:py:class:`Node` subclass)


==========
Beyond 1.0
==========

  - Aggregation
  - ``WITH``
  - Neo4J Built-in Functions
  - CASE expressions (CASE WHEN ... THEN ... ELSE ... END)
  - String Support (``STARTS WITH``, ``ENDS WITH``, =~)
