

********************
QueryBuilder Classes
********************

.. py:module:: neoalchemy.cypher

.. py:class:: CypherVerb

    Parent class to :py:class:`Create` and :py:class:`Match`.

    .. py:attribute:: params

        A dict mapping query parameter names to their current values.

    .. py:method:: CypherVerb.__str__

        Return the underlying Cypher query, which has been automatically
        parametrized.

    .. py:method:: delete(args=None, detach=False)

        Set the ``DELETE`` clause for the query.

    :param args: See the docs for :ref:`return-signature`.
    :param bool detach: If set, ``DETACH DELETE`` instead.
    :return: The object itself, to support :ref:`chaining`.

    .. py:method:: remove(args=None)

        Set the ``REMOVE`` clause for the query.

    :param args: See the docs for :ref:`return-signature`.
    :return: The object itself, to support :ref:`chaining`.

    .. py:method:: return_(args=None, distinct=False)

        Set the ``RETURN`` clause for the query.

    :param args: See the docs for :ref:`return-signature`.
    :param bool distinct: If set, ``RETURN DISTINCT`` instead.
    :return: The object itself, to support :ref:`chaining`.

    .. py:method:: set(property, value, var='n')

        Set a property to a value. Can be called multiple times.

    :param Property property: The property to set
    :param any value: The value of the property to set
    :param str var: The variable representing the node in Cypher.
    :return: The object itself, to support :ref:`chaining`.

    .. py:method:: where(expr, var='n', or_=False)

        Set the ``WHERE`` clause for the query.

    :param CypherExpression expr: See the docs for :ref:`cypher-expression`
    :param str var: The variable representing the node in Cypher.
    :param bool or\_: If set, this will be joined with the preceding ``WHERE``
                      clause using ``OR`` instead of ``AND``.
    :return: The object itself, to support :ref:`chaining`.


.. py:class:: Create(nodetype, var='n', unique=False, **params)

    :param NodeType nodetype: The NodeType used to construct the query.
    :param str var: The variable representing the node in Cypher.
    :param bool unique: If set, ``CREATE UNIQUE`` instead.


.. py:class:: Match(nodetype, var='n', optional=False, **params)

    :param NodeType nodetype: The NodeType used to construct the query.
    :param str var: The variable representing the node in Cypher.
    :param bool optional: If set, ``OPTIONAL MATCH`` instead.

    .. py:method:: Match.limit(n)

        Set the ``LIMIT`` clause for the query.

    :param int n: The argument to ``LIMIT``

    .. py:method:: Match.order_by(args, desc=False)

        Set the ``ORDER BY`` clause for the query.

    :param args: See the docs for :ref:`return-signature`.
    :param bool desc: If set, sort ``DESC``. Otherwise, sort ``ASC``.

    .. py:method:: Match.skip(n)

        Set the ``SKIP`` clause for the query.

    :param int n: The argument to ``SKIP``
