

**************
Schema Classes
**************

.. py:class:: Graph

    .. py:method:: delete_all

        Issues ``MATCH (all) DETACH DELETE all``, completely clearing the
        graph.

        It should go without saying that **this will delete all of your data!**

    .. py:attribute:: query(query, **params)

        Run an arbitrary query against the graph, with optional parameters.

        When not called, returns a reference to the Graph's :py:class:`Query`
        object.

    :param query: An object that stringifies to a Cypher query.
    :param params: The values for the query's parameters.
    :return: A Neo4J StatementResult corresponding to the issued query.
    :rtype: `neo4j.v1.StatementResult`_

    .. py:attribute:: schema

        A reference to the Graph's :py:class:`Schema` object.

    .. py:method:: session

        Returns `a session from the underlying driver`_'s pool.


.. py:class:: NodeType(label, *properties, extra_labels=())

    The core of the low-level QueryBuilder API. Represents a group of nodes
    with a common label and, optionally, common properties.

    :param str label: The primary label that defines the NodeType.
    :param Property properties: The :py:class:`Property` objects associated
                                with the NodeType.
    :param iterable extra_labels: Secondary labels shared by the NodeType.

    .. py:attribute:: LABEL

        The primary label that defines the NodeType.

    .. py:attribute:: labels

        The set of all labels shared by the NodeType's members.


.. py:class:: Property(name=None, type=str, default=None,\
                       indexed=False, unique=False, required=False)

    Represents an optionally constrained property on a :py:class:`NodeType`.

    :param str name: The name of the property on the node.
    :param callable type: Any callable used to convert a property value's type.
                          Typically a built-in Python type.
    :param default: The default value for the property if not specified.
    :param bool indexed: If set, `create an index`_ for the property.
    :param bool unique: If set, `create a unique constraint`_ for the property.
                        This implies ``indexed=True``.
    :param bool required: If set, `create a property existence constraint`_ for
                          the property. Only available with Neo4J Enterprise.


.. py:class:: Query

    .. py:method:: all

        Returns the result of ``MATCH (all) RETURN all``.

    .. py:method:: log(query, params)

        Log the given query and parameters. When not called, this property
        returns a :py:class:`QueryLog`, a subclass of :py:class:`OrderedDict`
        used for logging.


.. py:class:: Schema

    .. py:method:: Schema.add(nodetype, overwrite=False)

        Add a NodeType to the schema.

    :param NodeType nodetype: The NodeType instance to add to the schema
    :param bool overwrite: If set, DROP and re-CREATE any existing schema
    :rtype: None

    .. py:attribute:: Schema.constraints

        Get current graph constraints lazily.

        On first access, this fetches from the database. Afterwards, call
        :py:meth:`update()` to refresh.

    .. py:attribute:: Schema.indexes

        Get current graph indexes lazily.

        On first access, this fetches from the database. Afterwards, call
        :py:meth:`update()` to refresh.

    .. py:attribute:: Schema.labels

        Get current graph labels lazily.

        On first access, this fetches from the database. Afterwards, call
        :py:meth:`update()` to refresh.

    .. py:attribute:: Schema.ls

        Cypher statements for currently defined schema.

    .. py:method:: Schema.update

        Refresh constraints, indexes, and labels.


.. _a session from the underlying driver: https://neo4j.com/docs/developer-manual/current/#session
.. _neo4j.v1.StatementResult: https://neo4j.com/docs/developer-manual/current/#results
.. _create an index: https://neo4j.com/docs/developer-manual/current/#schema-index-create-an-index
.. _create a unique constraint: https://neo4j.com/docs/developer-manual/current/#query-constraints-unique-nodes
.. _create a property existence constraint: https://neo4j.com/docs/developer-manual/current/#query-constraints-prop-exist-nodes
