

********************
QueryBuilder Classes
********************

.. py:module:: neoalchemy.cypher

.. py:class:: SimpleQuery

    Parent class to :py:class:`Create`, :py:class:`Match`, and
    :py:class:`Merge`.

    .. py:attribute:: params

        A dict mapping query parameter names to their current values.

    .. py:method:: __str__

        Return the underlying Cypher query, which has been automatically
        parametrized.

    .. py:method:: delete(args=None, detach=False)

        Set the ``DELETE`` clause for the query.

    :param args: See the docs for :ref:`return-signature`.
    :param bool detach: If set, ``DETACH DELETE`` instead.
    :return: The object itself, to support :ref:`chaining`.

    .. py:method:: limit(n)

        Set the ``LIMIT`` clause for the query.

    :param int n: The argument to ``LIMIT``

    .. py:method:: order_by(args, desc=False)

        Set the ``ORDER BY`` clause for the query.

    :param args: See the docs for :ref:`return-signature`.
    :param bool desc: If set, sort ``DESC``. Otherwise, sort ``ASC``.

    .. py:method:: remove(args=None)

        Set the ``REMOVE`` clause for the query.

    :param args: See the docs for :ref:`return-signature`.
    :return: The object itself, to support :ref:`chaining`.

    .. py:method:: return_(args=None, distinct=False)

        Set the ``RETURN`` clause for the query.

    :param args: See the docs for :ref:`return-signature`.
    :param bool distinct: If set, ``RETURN DISTINCT`` instead.
    :return: The object itself, to support :ref:`chaining`.

    .. py:method:: set(property, value)

        Set a property to a value. Can be called multiple times.

    :param Property property: The property to set
    :param any value: The value of the property to set
    :return: The object itself, to support :ref:`chaining`.

    .. py:method:: skip(n)

        Set the ``SKIP`` clause for the query.

    :param int n: The argument to ``SKIP``

    .. py:method:: where(exprs, or_=False)

        Set the ``WHERE`` clause for the query.

    :param CypherExpression expr: See the docs for :ref:`cypher-expression`
    :param bool or\_: If set, this will be joined with the preceding ``WHERE``
                      clause using ``OR`` instead of ``AND``.
    :return: The object itself, to support :ref:`chaining`.


.. py:class:: Create(obj)

    :param GraphObject obj: The :py:class:`GraphObject` to create.


.. py:class:: Match(obj, optional=False)

    :param GraphObject obj: The :py:class:`GraphObject` to create.
    :param bool optional: If set, ``OPTIONAL MATCH`` instead.


.. py:class:: Merge(obj)

    :param GraphObject obj: The :py:class:`GraphObject` to create.

    .. :py:method:: on_create()

        Insert an ``ON CREATE`` where called.

    .. :py:method:: on_match()

        Insert an ``ON MATCH`` where called.
