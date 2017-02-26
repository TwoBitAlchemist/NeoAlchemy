

**********
Schema OGM
**********

The Schema OGM (Object Graph Mapper) allows you to use Python classes to specify
the structure of Nodes. We could make an OGM version of ``person`` like this::

    from neoalchemy import OGMBase, Property, Graph

    class Person(OGMBase):
        graph = Graph()

        name = Property(unique=True)
        age = Property(type=int)
        hair_color = Property()

We don't need to call :py:meth:`graph.schema.add` here; it is automatically
done for us by the OGMBase `metaclass`_.  **As soon as your class definition is
read into memory, the appropriate indexes and/or constraints are written to the
graph.** This is designed for convenient use in apps, especially in Frameworks
like `Flask`_, so that the graph is kept up to date as soon as your class is
imported for the first time.

If this behavior is undesired, it can be avoided by not attaching a graph
instance to the class until after it is created::

    class Person(OGMBase):
        name = Property(unique=True)
        age = Property(type=int)
        hair_color = Property()

    Person.graph = Graph()

If you do it this way, you must remember to write the schema yourself later
using :py:meth:`graph.schema.add`::

    Person.graph.schema.add(Person)

.. warning::
    From `the Neo4J Docs`_:

      Indexes in Neo4j are *eventually available*. That means that when you
      first create an index the operation returns immediately. The index is
      *populating* in the background and so is not immediately available for
      querying. When the index has been fully populated it will eventually
      come *online*. That means that it is now ready to be used in queries.


==============
Node Instances
==============

The ORM is built on top of :doc:`query-builder`, but uses several convenience
methods so that you don't have to build your own queries. When you instantiate,
you can choose between passing in parameter values to the constructor::

    person = Person(name='Ali', age=29, hair_color='red')

Or you can set them individually::

    person = Person()
    person.name, person.age = ('Ali', 29)
    person.hair_color = 'red'


------
Create
------

A node instance can be created on the graph like so::

    person.create()

This uses :doc:`query-builder` to :py:class:`~neoalchemy.cypher.Create` the
node with its currently set values.

.. note::
    If you set any parameter to ``None``, Neo4J will not create the property
    on the node. Likewise, setting any property to ``NULL`` is equivalent to
    removing it. This is a limitation of Cypher.


.. _metaclass: https://stackoverflow.com/q/100003/
.. _Flask: http://flask.pocoo.org/
.. _the Neo4J Docs: http://neo4j.com/docs/developer-manual/current/#graphdb-neo4j-schema-indexes
