

***********
ORM Classes
***********

The ORM is built around subclassing :py:class:`Node`.

.. py:class:: Node

    .. py:method:: Node.create(unique=False)

        Equivalent to calling :py:class:`~neoalchemy.cypher.Create` on the
        underlying :py:class:`NodeType` with params automatically set to the
        current node's :py:class:`Property` values.

    :param bool unique: If set, ``CREATE UNIQUE`` instead.
