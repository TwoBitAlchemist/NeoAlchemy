from collections import OrderedDict
from itertools import chain

from .operations import OperatorInterface


class Property(OperatorInterface):
    def __init__(self, name=None, type=str, default=None,
                 indexed=False, unique=False, required=False):
        self.__name = str(name) if name else None
        self.unique = bool(unique)
        self.indexed = self.unique or bool(indexed)
        self.required = bool(required)
        self.type = type
        self.default = default
        self.__value = self.value = None

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, value):
        if self.__name is not None:
            raise AttributeError("Can't change Property name once set.")
        self.__name = str(value)

    @property
    def schema(self):
        params = {
            'label': self.label,
            'lower_label': self.label.lower(),
            'name': self.__name,
        }

        schema = []
        if self.unique:
            constraint = ('CONSTRAINT ON ( %(lower_label)s:%(label)s ) '
                          'ASSERT %(lower_label)s.%(name)s IS UNIQUE')
            schema.append(constraint % params)
        elif self.indexed:
            schema.append('INDEX ON :%(label)s(%(name)s)' % params)

        if self.required:
            constraint = ('CONSTRAINT ON ( %(lower_label)s:%(label)s ) '
                          'ASSERT exists(%(lower_label)s.%(name)s)')
            schema.append(constraint % params)

        return schema

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        if value is None:
            value = self.default() if callable(self.default) else self.default
        if value is not None:
            value = self.type(value)
        self.__value = value


class NodeType(object):
    def __init__(self, label, *properties, **kw):
        self.__labels = (label,) + tuple(kw.get('extra_labels', ()))
        self.__properties = OrderedDict()
        for prop in properties:
            if not isinstance(prop, Property):
                raise TypeError("Must be a Property object. "
                                "'%s' given." % prop.__class__)
            prop.label = label
            if prop.name in self.__properties:
                raise ValueError("Duplicate property found: '%s'" % prop.name)

            self.__properties[prop.name] = prop

    @property
    def LABEL(self):
        return self.__labels[0]

    @property
    def labels(self):
        return self.__labels

    @property
    def schema(self):
        return [s for p in self.__properties.values() for s in p.schema]

    @property
    def properties(self):
        return self.__properties

    def __getattr__(self, attr):
        try:
            return self.__properties[attr]
        except KeyError:
            super(NodeType, self).__getattribute__(attr)
