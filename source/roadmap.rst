

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
  - :py:meth:`neoalchemy.OGMBase.match` / :py:meth:`neoalchemy.OGMBase.merge`
  - Schema OGM Basic Relation support
  - ``WITH``
  - Neo4J Built-in Functions
  - Arbitrary Relationship Depth support in Schema OGM
  - Hydrate: ``neo4j.v1.StatementResult`` => Schema OGM class
    (:py:class:`OGMBase` subclass)
  - Aggregation


===
1.0
===

  - To be determined


==========
Beyond 1.0
==========

  - Smarter queries
  - CASE expressions (CASE WHEN ... THEN ... ELSE ... END)
  - String Support (``STARTS WITH``, ``ENDS WITH``, =~)
