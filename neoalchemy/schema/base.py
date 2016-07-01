from collections import OrderedDict

from .operations import OperatorInterface


class Property(OperatorInterface):
    def __init__(self, name=None, type=str, default=None,
                 indexed=False, unique=False, required=False):
        self.__name = name or str(name)
        self.unique = bool(unique)
        self.indexed = self.unique or bool(indexed)
        self.required = bool(required)
        self.type = type
        self.default = default

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, value):
        if self.__name is not None:
            raise AttributeError("Can't change Property name once set.")
        self.__name = str(value)

    def __str__(self):
        label, name = self.label, self.__name
        schema = []
        if self.unique:
            schema.append('CREATE CONSTRAINT ON (n:%s) '
                          'ASSERT n.%s IS UNIQUE' % (label, name))
        elif self.indexed:
            schema.append('CREATE INDEX ON :%s(%s)' % (label, name))

        if self.required:
            schema.append('CREATE CONSTRAINT ON (n:%s) '
                          'ASSERT exists(n.%s)' % (label, name))
        return '\n'.join(schema)


class NodeType(object):
    def __init__(self, label, *properties, **kw):
        self.__labels = (label,) + tuple(kw.get('extra_labels', ()))
        self.__schema = OrderedDict()
        for prop in properties:
            if not isinstance(prop, Property):
                raise TypeError("Must be a Property object. "
                                "'%s' given." % prop.__class__)
            prop.label = label
            if prop.name in self.__schema:
                raise ValueError("Duplicate property found: '%s'" % prop.name)

            self.__schema[prop.name] = prop

    @property
    def LABEL(self):
        return self.__labels[0]

    @property
    def labels(self):
        return self.__labels

    @property
    def schema(self):
        return self.__schema

    def __getattr__(self, attr):
        try:
            return self.__schema[attr]
        except KeyError:
            super().__getattribute__(attr)

    def __str__(self):
        return '\n'.join(filter(bool, map(str, self.__schema.values())))
