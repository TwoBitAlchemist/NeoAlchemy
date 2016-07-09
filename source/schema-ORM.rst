

**********
Schema ORM
**********

We could make an ORM version of ``Person`` like this::

    from neoalchemy import Node, Property, Graph

    class Person(Node):
        graph = Graph()

        name = Property(unique=True)
        age = Property(type=int)
        hair_color = Property()

Note that this subclasses :py:class:`Node`, not :py:class:`NodeType`. We don't
need to call :py:meth:`graph.schema.add` here; it is automatically done for us
by Node's `metaclass`_.  **As soon as your class definition is read into
memory, the appropriate indexes and/or constraints are written to the graph.**
This is designed for convenient use in apps, especially in Frameworks like
`Flask`_, so that the graph is kept up to date as soon as your class is
imported for the first time.

If this behavior is undesired, it can be avoided by not attaching a graph
instance to the class until after it is created::

    class Person(Node):
        name = Property(unique=True)
        age = Property(type=int)
        hair_color = Property()

    Person.graph = Graph()

If you do it this way, you must remember to write the schema yourself later
using :py:meth:`graph.schema.add` on the underlying :py:class:`NodeType`::

    Person.graph.schema.add(Person.__nodetype__)


.. _metaclass: https://stackoverflow.com/q/100003/
.. _Flask: http://flask.pocoo.org/
