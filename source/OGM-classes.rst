

***********
OGM Classes
***********

The OGM is built around subclassing :py:class:`OGMBase`.

.. py:class:: OGMBase

    .. py:attribute:: __node__

        The underlying :py:class:`Node` representing this OGM class.

    .. py:method:: bind(*keys)

        Equivalent to ``self.__node__.bind(*keys)``.

    .. py:attribute:: bound_keys

        Equivalent to ``self.__node__.bound_keys``.

    .. py:attribute:: is_bound

        Equivalent to ``self.__node__.is_bound``.
