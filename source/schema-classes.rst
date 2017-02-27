

**************
Schema Classes
**************

.. py:class:: GraphObject(graph=None, **properties)

    The base class for :py:class:`Node` and :py:class:`Relationship`

    :param Graph graph: The graph instance to which the object should write.
    :param str var: The Cypher variable representing the object.
    :param Property properties: The :py:class:`Property` objects associated
                                with the Node. String arguments are
                                automatically converted into Property objects
                                of the default string type.

    .. py:method:: bind(*keys)

    :param str keys: The names of properties to bind to. If none are provided,
                     the default is to bind to all Properties marked as
                     primary keys, if any.

    .. py:attribute:: bound_keys

        A tuple representing the keys to which the object is currently bound.

    .. py:attribute:: is_bound

        A boolean indicating whether or not the object is bound. This can be
        True even if bound_keys is empty.

    .. py:attribute:: properties

        A dict representing properties and their current values. **Note that
        editing this dict does not set properties!**

    .. py:method:: items()

        A dict-like method providing a tuple of pairs of property names and
        :py:class:`Property` objects.

    .. py:method:: keys()

        A dict-like method providing a tuple of names of attributes which
        correspond to Properties.

    .. py:method:: values()

        A dict-like method providing a tuple of :py:class:`Property` objects
        defined for the object.

.. py:class:: Node(*labels, **properties)

    The core of the low-level QueryBuilder API. Represents a Node in Neo4J
    along with its labels and properties.

    :param str labels: The labels for the Node. These should be defined from
                       least to most specific.
    :param str var: The Cypher variable representing the node.
    :param Property properties: The :py:class:`Property` objects associated
                                with the Node. String arguments are
                                automatically converted into Property objects
                                of the default string type.

    .. py:attribute:: type

        The primary label that defines the Node.

    .. py:attribute:: labels

        The set of all labels shared by the Node's members.


.. py:class:: Relationship(type, start_node=None, end_node=None, depth=None,\
                           directed=True, var='rel', **properties)

    :param str type: The relationship's type, which in NeoAlchemy is required.
    :param Node start_node: The node represented by a, in ``(a)-[:TYPE]->(b)``.
    :param Node end_node: The node represented by b, in ``(a)-[:TYPE]->(b)``.
    :param depth: A variable property to control the depth of the relationship
                  when used as part of a Cypher statement. ``-1`` indicates
                  "infinite" depth (``*``), any positive integer ``n``
                  represents that depth (``*n``), and any tuple of positive
                  integers ``(m, n)`` represents a range (``*m..n``).
    :param bool directed: Whether or not the relation is directed. Default
                          is True (directed relation). Note that some
                          operations (such as merge) become effectively
                          arbitrary on undirected relationships. This is a
                          limitation of Neo4J.
    :param str var: The Cypher variable representing the relationship.
    :param Property properties: The :py:class:`Property` objects associated
                                with the Node. String arguments are
                                automatically converted into Property objects
                                of the default string type.

    .. :py:method:: exists(exists=True)

        Returns a CypherExpression (which can be used with
        :py:method::`~neoalchemy.cypher.SimpleQuery.where`)
        corresponding to the ``EXISTS`` function in Cypher.

    :param bool exists: If False, do ``NOT EXISTS`` instead. Default is True.


.. py:class:: Property(obj=None, type=str, default=None, value=None,\
                       indexed=False, unique=False, required=False,\
                       primary_key=False, read_only=False)

    Represents an optionally constrained property on a :py:class:`GraphObject`.

    :param GraphObject obj: The object to which the Property will be bound.
    :param callable type: Any callable used to convert a property value's type.
                          Typically a built-in Python type or something found
                          in the ``neoalchemy.validators`` module.
    :param default: The default value for the property if not specified. This
                    can be a callable. Either the value (or the return value
                    if callable) must pass validation given by type.
    :param value: The starting value for the property. Must pass validation
                  given by type.
    :param bool indexed: If set, `create an index`_ for the property.
    :param bool unique: If set, `create a unique constraint`_ for the property.
                        This implies ``indexed=True``.
    :param bool required: If set, `create a property existence constraint`_ for
                          the property. Only available with Neo4J Enterprise.
    :param bool primary_key: If set, the property is one of the object's
                             default bindings when
                             :py:method::`~neoalchemy.GraphObject.bind`
                             is called with no arguments.
    :param bool read_only: Not yet implemented.

    .. py:attribute:: value

        The current value of the property.

    .. py:attribute:: var

        The current Cypher variable for the property. A property must be
        bound to a :py:class:`GraphObject` to compute its Cypher variable.


.. py:class:: Graph

    .. py:method:: delete_all

        Issues ``MATCH (all) DETACH DELETE all``, completely clearing the
        graph.

        It should go without saying that **this will delete all of your data!**

    .. py:attribute:: query(query, **params)

        Run an arbitrary query against the graph, with optional parameters.

        When not called, returns a reference to the Graph's
        :py:class:`graph.query` object.

    :param query: An object that stringifies to a Cypher query.
    :param params: The values for the query's parameters.
    :return: A Neo4J StatementResult corresponding to the issued query.
    :rtype: `neo4j.v1.StatementResult`_

    .. py:attribute:: schema

        A reference to the Graph's :py:class:`graph.schema` object.

    .. py:method:: session

        Returns `a session from the underlying driver`_'s pool.


.. py:class:: graph.query

    .. py:method:: graph.query.all

        Returns the result of ``MATCH (all) RETURN all``.

    .. py:method:: graph.query.log(query, params)

        Log the given query and parameters. For other options, see
        :py:class:`graph.query.log`.


.. py:class:: graph.query.log

    .. py:attribute:: MAX_SIZE

        *int* The maximum number of log entries to store.


.. py:class:: graph.schema

    .. py:method:: graph.schema.add(nodetype, overwrite=False)

        Add a NodeType to the schema.

    :param NodeType nodetype: The NodeType instance to add to the schema
    :param bool overwrite: If set, DROP and re-CREATE any existing schema
    :rtype: None

    .. py:attribute:: graph.schema.constraints

        Get current graph constraints lazily.

        On first access, this fetches from the database. Afterwards, call
        :py:meth:`update()` to refresh.

    .. py:attribute:: graph.schema.indexes

        Get current graph indexes lazily.

        On first access, this fetches from the database. Afterwards, call
        :py:meth:`update()` to refresh.

    .. py:attribute:: graph.schema.labels

        Get current graph labels lazily.

        On first access, this fetches from the database. Afterwards, call
        :py:meth:`update()` to refresh.

    .. py:attribute:: graph.schema.ls

        Cypher statements for currently defined schema.

    .. py:method:: graph.schema.update

        Refresh constraints, indexes, and labels.


.. _a session from the underlying driver: https://neo4j.com/docs/developer-manual/current/drivers/run-statements/#_sessions
.. _neo4j.v1.StatementResult: https://neo4j.com/docs/api/python-driver/current/session.html?highlight=statementresult#neo4j.v1.StatementResult
.. _create an index: https://neo4j.com/docs/developer-manual/current/cypher/schema/index/
.. _create a unique constraint: https://neo4j.com/docs/developer-manual/current/cypher/schema/constraints/
.. _create a property existence constraint: https://neo4j.com/docs/developer-manual/current/#query-constraints-prop-exist-nodes
