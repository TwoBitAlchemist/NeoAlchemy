

********************
The QueryBuilder API
********************

The QueryBuilder API allows you to express familiar Cypher queries using normal
Python objects and operators. To demonstrate it, we will use a simple
:py:class:`NodeType` like the ``user`` we defined in the previous section.
We'll call this one ``Person`` and give it a few simple characteristics::

    from neoalchemy import NodeType, Property

    Person = NodeType('Person',
        Property('name', indexed=True),
        Property('age', type=int),
        Property('hair_color')
    )


======
Create
======

NeoAlchemy features :doc:`querybuilder-classes` which correspond to `familiar
Cypher verbs`_. These are located in the :py:mod:`neoalchemy.cypher` module::

    from neoalchemy.cypher import Create

Let's start by constructing about the simplest query possible::

    create = Create(Person)

We can see the query this generates by printing it::

    >>> print(create)
    CREATE (n:Person {age: {age_n}, name: {name_n}, hair_color: {hair_color_n}})

NeoAlchemy has automatically applied the ``Person`` label and created
parameters associated with each of the properties we defined. We can see
the current values for each parameter by inspecting the
:py:attr:`~CypherVerb.params` dict::

    >>> create.params
    {'age_n': None, 'hair_color_n': None, 'name_n': None}

Each parameter is named according to its associated property and the variable
representing its associated node in the underlying Cypher. By Neo4J convention,
the default parameter is ``n``. This can be freely changed to whatever you like
by specifying a second argument to :py:class:`Create`::

    >>> create = Create(Person, 'm')
    >>> print(create)
    CREATE (m:Person {age: {age_m}, name: {name_m}, hair_color: {hair_color_m}})

This is an important feature which will come in handy when specifying more
complex queries, as we will see later.

Properties can either be set one at a time using :py:meth:`~CypherVerb.set`::

    create = Create(Person).set(Person.hair_color, 'red')

Or set directly using the :py:attr:`~CypherVerb.params` dict::

    >>> create.params['name_n'] = 'Ali'
    >>> ali_params = {'age_n': 29, 'hair_color_n': 'red'}
    >>> create.params.update(ali_params)


Once you're satisfied with your settings, you can write it to the graph using
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

    from neoalchemy.cypher import Match

Match has a very similar interface to Create. For a simple use case, we get
almost identical results::

    >>> match = Match(Person)
    >>> print(match)
    MATCH (n:Person {hair_color: {hair_color_n}, name: {name_n}, age: {age_n}})

...but this isn't a very interesting ``MATCH`` statement. For one thing, it's
not a full query yet. In order to make this useful, at a minimum we need to
return something::

    >>> print(match.return_())
    MATCH (n:Person {hair_color: {hair_color_n}, name: {name_n}, age: {age_n}}) RETURN *

.. note::
    Notice the function is **return_**, not **return**. The latter would cause
    a syntax error since ``return`` is a Python reserved word.

.. _return-signature:

------
Return
------

If you call :py:meth:`~CypherVerb.return_` with no arguments, the resulting
query will ``RETURN *``, returning everything you have matched. `For
performance reasons`_, however, this is often not the best choice. There are
several ways to return only what you need instead of everything you've touched.

============================  ==========================================  ========================
 What to Return                NeoAlchemy                                  Cypher Equivalent
============================  ==========================================  ========================
 One node                      ``return_('node')``                         ``RETURN node``
 Many nodes                    ``return_(['n', 'm'])``                     ``RETURN n, m``
 One property                  ``return_({'n': 'name'})``                  ``RETURN n.name``
 Many properties               ``return_({'n': ['x', 'y']})``              ``RETURN n.x, n.y``
 Nodes with properties         ``return_({'m': 'x', 'n': 'y'})``           ``RETURN m.x, n.y``
 Nodes with many properties    ``return_({'m': 'x', 'n': ['y', 'z']})``    ``RETURN m.x, n.y, n.z``
============================  ==========================================  ========================

.. note::
    The :py:meth:`~CypherVerb.remove` and :py:meth:`~CypherVerb.delete` methods
    work the same way. They correspond to Cypher's `REMOVE`_ and `DELETE`_.

.. _cypher-expression:

-----
Where
-----

As with :py:meth:`~CypherVerb.set`, the :py:meth:`~CypherVerb.where` method can
be used to set parameters one at a time::

    match = Match(Person).where(Person.name=='Ali')

The first argument to ``where`` is a ``CypherExpression`` object, which is
automatically created when you perform the corresponding Python comparison
using one of the NodeType's Properties.

=======================  =============================  =======================
 Comparison Type          NeoAlchemy CypherExpression    Cypher Equivalent
=======================  =============================  =======================
 Equal to                 ``Person.name == 'Ali'``       ``n.name = 'Ali'``
 Not equal to             ``Person.name != 'Ali'``       ``n.name <> 'Ali'``
 Greater than             ``Person.age > 29``            ``n.age > 29``
 Greater than or equal    ``Person.age >= 29``           ``n.age >= 29``
 Lesser than              ``Person.age < 29``            ``n.age < 29``
 Lesser than or equal     ``Person.age <= 29``           ``n.age <= 29``
=======================  =============================  =======================

.. _chaining:

--------
Chaining
--------


.. _familiar Cypher verbs: https://neo4j.com/docs/developer-manual/current/#query-create
.. _Neo4J StatementResult: https://neo4j.com/docs/api/python-driver/current/#neo4j.v1.StatementResult
.. _For performance reasons: https://neo4j.com/docs/developer-manual/current/#query-tuning
.. _REMOVE: https://neo4j.com/docs/developer-manual/current/#query-remove
.. _DELETE: https://neo4j.com/docs/developer-manual/current/#query-delete
