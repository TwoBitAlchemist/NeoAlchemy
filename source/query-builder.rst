

********************
The QueryBuilder API
********************

.. note::
    If you don't need the QueryBuilder API, feel free to skip straight to
    learning about the :doc:`schema-OGM`.

The QueryBuilder API allows you to express familiar Cypher queries using normal
Python objects and operators. To demonstrate it, we will use a simple
:py:class:`Node` like the ``user`` we defined in the previous section.
We'll call this one ``person`` and give it a few simple characteristics::

    from neoalchemy import Node, Property

    person = Node('Person',
        name=Property(indexed=True),
        age=Property(type=int),
        hair_color=Property()
    )

Don't forget to create the indexes and constraints you specified using
:py:meth:`graph.schema.add`::

    graph.schema.add(person)

.. warning::
    From `the Neo4J Docs`_:

      Indexes in Neo4j are *eventually available*. That means that when you
      first create an index the operation returns immediately. The index is
      *populating* in the background and so is not immediately available for
      querying. When the index has been fully populated it will eventually
      come *online*. That means that it is now ready to be used in queries.


======
Create
======

NeoAlchemy features :doc:`querybuilder-classes` which correspond to `familiar
Cypher verbs`_::

    from neoalchemy import Create

Let's start by constructing perhaps the simplest query possible::

    create = Create(person)

We can see the query this generates by printing it::

    >>> print(create)
    CREATE (node:`Person`)
        SET node.name = {node_name}, node.age = {node_age}, node.hair_color = {node_hair_color}

NeoAlchemy has automatically applied the ``Person`` label and created
parameters associated with each of the properties we defined. We can see
the current values for each parameter by inspecting the
:py:attr:`~neoalchemy.cypher.SimpleQuery.params` dict::

    >>> create.params
    {'node_age': None, 'node_hair_color': None, 'node_name': None}

Each parameter is named according to its associated property and the variable
representing its associated node in the underlying Cypher. The default node
variable is ``node``. This can be freely changed to whatever you like::

    >>> person.var = 'n'
    >>> print(Create(person))
    CREATE (n:`Person`)
        SET n.name = {n_name}, n.age = {n_age}, n.hair_color = {n_hair_color}

Properties can be set individually on the Node::

    >>> person.name = 'Ali'
    >>> person.age = 30
    >>> person.hair_color = 'red'

Once you're satisfied, you can write it to the graph using
:py:class:`graph.query`::

    >>> graph.query(create, **create.params)

.. note::
    You can run arbitrary queries against the database using
    :py:class:`graph.query`.  It takes a string as its first argument and
    accepts parameters as keyword arguments. It returns a `Neo4J
    StatementResult`_. We'll learn more in depth about what :py:class:`Graph`
    can do a little later.


=====
Match
=====

Now that we've experimented a bit with writing to the database, let's take a
look at how to read data from it::

    from neoalchemy import Match

Match has a very similar interface to Create. In the simplest case, Match looks
only at labels::

    >>> match = Match(person)
    >>> print(match)
    MATCH (n:`Person`)

...but this isn't a full query yet. In order to make this useful, we need to
return something::

    >>> print(match.return_())
    MATCH (n:`Person`)
    RETURN *

.. note::
    Notice the function is **return_**, not **return**. The latter would cause
    a syntax error since ``return`` is a reserved word in Python.

.. _return-signature:

------
Return
------

If you call :py:meth:`~neoalchemy.cypher.SimpleQuery.return_` with no arguments,
the resulting query will ``RETURN *``, returning everything you have matched.
`For performance reasons`_, however, this is often not the best choice. There
are several ways to return only what you need instead of everything you've
touched.

============================  ==========================================  ========================
 What to Return                NeoAlchemy                                  Cypher Equivalent
============================  ==========================================  ========================
 One node                      ``return_(person_n)``                       ``RETURN n``
 Many nodes                    ``return_(person_n, person_m)``             ``RETURN n, m``
 One property                  ``return_(person_n['name'])``               ``RETURN n.name``
 Many properties               ``return_(person_n['x'], person_n['y'])``   ``RETURN n.x, n.y``
 Many nodes and properties     ``return_(person_m['x'], person_n['y'])``   ``RETURN m.x, n.y``
============================  ==========================================  ========================

.. note::
    The :py:meth:`~neoalchemy.cypher.SimpleQuery.remove` and
    :py:meth:`~neoalchemy.cypher.SimpleQuery.delete` methods work the same way.
    They correspond to Cypher's `REMOVE`_ and `DELETE`_. Also note that, unlike
    in pure Cypher, ``REMOVE`` cannot be used to remove labels through the
    NeoAlchemy APIs.

.. _cypher-expression:

-----
Where
-----

As with :py:meth:`~neoalchemy.cypher.SimpleQuery.set`, the
:py:meth:`~neoalchemy.cypher.SimpleQuery.where` method can be used to set
parameters one at a time::

    match = Match(person).where(person['name']=='Ali')

The first argument is a :py:class:`CypherExpression` object, which is
automatically created when you perform the corresponding Python comparison
using one of the NodeType's Properties.

=======================  =============================  =======================
 Comparison Type          NeoAlchemy CypherExpression    Cypher Equivalent
=======================  =============================  =======================
 Equal to                 ``person['name'] == 'Ali'``    ``n.name = 'Ali'``
 Not equal to             ``person['name'] != 'Ali'``    ``n.name <> 'Ali'``
 Greater than             ``person['age'] > 29``         ``n.age > 29``
 Greater than or equal    ``person['age'] >= 29``        ``n.age >= 29``
 Lesser than              ``person['age'] < 29``         ``n.age < 29``
 Lesser than or equal     ``person['age'] <= 29``        ``n.age <= 29``
=======================  =============================  =======================

.. _chaining:

========
Chaining
========

An important concept in NeoAlchemy is method chaining. Most methods ``return
self`` so you can call them like so::

    match = Match(person).where(person['name']=='Ali').return_(person['name'])

This makes for convenient and expressive one-liners. However, this also means
that state is easy to build up over time and as part of larger algorithms::

    match = Match(person)
    # ... some code ...
    match.where(person['age']=age)
    # ... more code...
    match.return_(ret_params)

.. _binding:

======================
Binding & Primary Keys
======================

Often instead of specifying individual where clauses, it will be preferable to
match on a set of the Node's Properties that define what it is. One way to do
this in NeoAlchemy is by *binding* the Node to those Properties::

    >>> print(Match(person))
    MATCH (n:`Person`)
    >>> ali = Node('Person', name='Ali', var='n')
    >>> print(Match(ali.bind('name')))
    MATCH (n:`Person`)
        WHERE n.name = {n_name}

Setting certain Properties as the *primary keys* of a Node will give it a
default binding::

   >>> person = Node('Person', name=Property(primary_key=True), var='n')
   >>> print(Match(person.bind()))
    MATCH (n:`Person`)
        WHERE n.name = {n_name}

=============
Relationships
=============

So far, we have only worked with nodes. NeoAlchemy also provides a
:py:class:`Relationship` class. Relationships in NeoAlchemy always have a
type. To create a relationship::

    >>> from neoalchemy import Relationship
    >>> knows = Relationship('KNOWS')

Relationships aren't much good without start and end nodes, though. Let's
connect two Person nodes who know each other::

   >>> knows.start_node = person.copy(var='a')
   >>> knows.end_node = person.copy(var='b')
   >>> print(Create(knows))
   CREATE (a)-[rel:`KNOWS`]->(b)

But wait! This isn't the right Cypher query. In order to use relationships
with Cypher query builders, we must first build up match statements to grab
the right end nodes.

================
Set Combinations
================

Not all Cypher queries are one line, and neither are all NeoAlchemy queries.
You can use Python's set operators to combine several NeoAlchemy objects into
multi-line queries before returning. The ``&`` (`set intersection`_) operator
is used for line-by-line cominbation. The most typical way this will be used
is with relationships in order to fully specify them for Creating or Matching::

    >>> ali = Node('Person', name='Ali', var='ali').bind('name')
    >>> frank = Node('Person', name='Frank', var='frank').bind('name')
    >>> knows = Relationship('KNOWS', ali, frank)
    >>> print(Match(ali) & Match(frank) & Match(knows))
    MATCH (ali:`Person`)
        WHERE ali.name = {ali_name}
    MATCH (frank:`Person`)
        WHERE frank.name = {frank_name}
    MATCH (ali)-[rel:`KNOWS`]->(frank)

The ``|`` (`set union`_) operator is used for ``UNION ALL``. To borrow an
example from the Cypher docs::

    >>> movie = Node('Movie', title=Property(primary_key=True), var='movie')
    >>> actor = Node('Actor', name=Property(primary_key=True), var='actor')
    >>> acted_in = Relationship('ACTED_IN', actor, movie)
    >>> directed = Relationship('DIRECTED', actor, movie)
    >>> actor_match = (
    ...     (Match(actor) & Match(movie) & Match(acted_in))
    ...      .return_(actor['name'], movie['title'])
    ... )
    >>> director_match = (
    ...     (Match(actor) & Match(movie) & Match(directed))
    ...      .return_(actor['name'], movie['title'])
    ... )
    >>> print(actor_match | director_match)
    MATCH (actor:`Actor`)
    MATCH (movie:`Movie`)
    MATCH (actor)-[rel:`ACTED_IN`]->(movie)
    RETURN actor.name, movie.title
    UNION ALL
    MATCH (actor:`Actor`)
    MATCH (movie:`Movie`)
    MATCH (actor)-[rel:`DIRECTED`]->(movie)
    RETURN actor.name, movie.title

If you instead want ``UNION``, use the ``^`` (`exclusive or`_) operator.

.. note::
    ``UNION`` must be performed on queries with very similar result structures.
    You must take this into account when building your queries.


.. _the Neo4J Docs: http://neo4j.com/docs/developer-manual/current/#graphdb-neo4j-schema-indexes
.. _familiar Cypher verbs: https://neo4j.com/docs/developer-manual/current/cypher/clauses/
.. _Neo4J StatementResult: https://neo4j.com/docs/api/python-driver/current/session.html?highlight=statementresult#neo4j.v1.StatementResult
.. _For performance reasons: https://neo4j.com/docs/developer-manual/current/cypher/query-tuning
.. _REMOVE: https://neo4j.com/docs/developer-manual/current/cypher/clauses/remove/
.. _DELETE: https://neo4j.com/docs/developer-manual/current/cypher/clauses/delete/
.. _set intersection: https://docs.python.org/3/library/stdtypes.html#set.intersection
.. _set union: https://docs.python.org/3/library/stdtypes.html#set.union
.. _exclusive or: https://docs.python.org/3/library/stdtypes.html#set.symmetric_difference
