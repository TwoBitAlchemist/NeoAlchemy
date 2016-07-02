

The QueryBuilder API
====================

The QueryBuilder API allows you to express familiar Cypher queries using normal
Python objects and operators. To demonstrate it, we will use a simple
``NodeType`` like the ``user`` we defined in the previous section. We'll call
this one ``Person`` and give it a few simple characteristics::

    from neoalchemy import NodeType, Property

    Person = NodeType('Person',
        Property('name', indexed=True),
        Property('age', type=int),
        Property('hair_color')
    )


Create
------

NeoAlchemy features several classes which correspond to `familiar Cypher
verbs`_. These are located in the ``neoalchemy.cypher`` module::

    from neoalchemy.cypher import Create

Let's start by constructing about the simplest query possible::

    create = Create(Person)

We can see the query this generates by printing it::

    >>> print(create)
    CREATE (n:Person {age: {age_n}, name: {name_n}, hair_color: {hair_color_n}})

NeoAlchemy has automatically applied the ``Person`` label and created
parameters associated with each of the ``Properties`` we defined. We can see
the current values for each parameter by inspecting the ``params`` dict::

    >>> create.params
    {'age_n': None, 'hair_color_n': None, 'name_n': None}

Each parameter is named according to its associated property and the variable
representing its associated node in the underlying Cypher. By Neo4J convention,
the default parameter is ``n``. This can be freely changed to whatever you like
by specifying a second argument to ``Create``::

    >>> create = Create(Person, 'm')
    >>> print(create)
    CREATE (m:Person {age: {age_m}, name: {name_m}, hair_color: {hair_color_m}})

This is an important feature which will come in handy when specifying more
complex queries, as we will see later.

Properties can either be set one at a time using ``set``::

    create = Create(Person).set(Person.hair_color, 'red')

Or set directly using the ``params`` dict::

    >>> create.params['name_n'] = 'Ali'
    >>> ali_params = {'age_n': 29, 'hair_color_n': 'red'}
    >>> create.params.update(ali_params)


Once you're satisfied with your settings, you can write it to the graph using
``graph.query``::

    >>> graph.query(create, **create.params)

.. note::
    You can run arbitrary queries against the database using ``graph.query``.
    It takes a string as its first argument and accepts parameters as keyword
    arguments. It returns a `Neo4J StatementResult`_. We'll learn more in depth
    about what the ``Graph`` class can do a little later.


.. _familiar Cypher verbs: https://neo4j.com/docs/developer-manual/current/#query-create
.. _Neo4J StatementResult: https://neo4j.com/docs/api/python-driver/current/#neo4j.v1.StatementResult
