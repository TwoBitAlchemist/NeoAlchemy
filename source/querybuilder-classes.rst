

********************
QueryBuilder Classes
********************

.. py:class:: Create(nodetype, var='n', unique=False, **params)

    :param NodeType nodetype: The NodeType used to construct the query.
    :param str var: The variable representing the node in Cypher.
    :param bool unique: If set, ``CREATE UNIQUE`` instead.

    .. py:attribute:: Create.params

        A dict mapping query parameter names to their current values or
        ``None``.

    .. py:method:: Create.__str__

        Return the underlying ``CREATE`` query, which has been automatically
        parametrized.

    .. py:method:: Create.set(property, value, var='n')

        Set a property to a value. Can be called multiple times.

    :param Property property: The property to set
    :param any value: The value of the property to set
    :param str var: The variable representing the node in Cypher.
    :return: The Create object, to support chaining.
    :rtype: :py:class:`Create`

    .. py:method:: Create.delete(args=None)

        Set the ``DELETE`` clause for the query.

    :param args: The way this is handled is explained in the
                 :ref:`return-signature` docs.
    :return: The Create object, to support chaining.
    :rtype: :py:class:`Create`

    .. py:method:: Create.remove(args=None)

        Set the ``REMOVE`` clause for the query.

    :param args: The way this is handled is explained in the
                 :ref:`return-signature` docs.
    :return: The Create object, to support chaining.
    :rtype: :py:class:`Create`

    .. py:method:: Create.return_(args=None, distinct=False)

        Set the ``RETURN`` clause for the query.

    :param args: Parsed according to :ref:`return-signature`
    :return: The Create object, to support chaining.
    :rtype: :py:class:`Create`


.. py:class:: Match(nodetype, var='n', optional=False, **params)

    :param NodeType nodetype: The NodeType used to construct the query.
    :param str var: The variable representing the node in Cypher.
    :param bool optional: If set, ``OPTIONAL MATCH`` instead.

    .. py:attribute:: Match.params

        A dict mapping query parameter names to their current values.

    .. py:method:: Match.__str__

        Return the underlying ``MATCH`` query, which has been automatically
        parametrized.

    .. py:method:: Match.delete(args=None)

        Set the ``DELETE`` clause for the query.

    :param args: The way this is handled is explained in the
                 :ref:`return-signature` docs.
    :return: The Match object, to support chaining.
    :rtype: :py:class:`Match`

    .. py:method:: Match.remove(args=None)

        Set the ``REMOVE`` clause for the query.

    :param args: The way this is handled is explained in the
                 :ref:`return-signature` docs.
    :return: The Match object, to support chaining.
    :rtype: :py:class:`Match`

    .. py:method:: Match.return_(args=None, distinct=False)

        Set the ``RETURN`` clause for the query.

    :param args: The way this is handled is explained in the
                 :ref:`return-signature` docs.
    :param bool distinct: If set, ``RETURN DISTINCT`` instead.
    :return: The Match object, to support chaining.
    :rtype: :py:class:`Match`

    .. py:method:: Match.where(expr, var='n', or_=False)

        Set the ``WHERE`` clause for the query.

    :param CypherExpression expr: See the docs for :py:class:`CypherExpression`
    :param str var: The variable representing the node in Cypher.
    :param bool or\_: If set, this will be joined with the preceding ``WHERE``
                      clause using ``OR`` instead of ``AND``.
    :return: The Match object, to support chaining.
    :rtype: :py:class:`Match`
