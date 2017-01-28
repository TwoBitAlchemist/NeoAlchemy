from collections import OrderedDict
from itertools import chain

import six

from .operations import OperatorInterface


class ImmutableAttributeError(AttributeError):
    def __init__(self, name, obj):
        error = "Can't reset immutable attribute '%s' on %s object."
        cls = obj.__class__.__name__
        super(ImmutableAttributeError, self).__init__(error % (name, cls))


class SetOnceDescriptor(object):
    def __init__(self, class_, name):
        self.name = name
        self.values = dict()

    def __get__(self, instance, owner):
        if instance is None:
            return getattr(owner, self.name)

        return self.values.get(id(instance))

    def __set__(self, instance, value):
        if self.values.get(id(instance)) is not None:
            raise ImmutableAttributeError(self.name, instance)

        self.values[id(instance)] = value

    def __delete__(self, instance):
        raise ImmutableAttributeError(self.name, instance)


class PropertyMeta(type):
    def __init__(cls, class_name, bases, attrs):
        for attr in ('name', 'type', 'unique', 'indexed', 'required',
                     'primary_key', 'read_only'):
            setattr(cls, attr, SetOnceDescriptor(cls, attr))
        super(PropertyMeta, cls).__init__(class_name, bases, attrs)


@six.add_metaclass(PropertyMeta)
class Property(OperatorInterface):
    def __init__(self, name=None, obj=None, type=str, default=None,
                 indexed=False, unique=False, required=False,
                 primary_key=False, read_only=False):
        self.name = str(name) if name else None
        self.__obj = self.obj = obj
        self.type = type

        self.unique = bool(unique)
        self.indexed = self.unique or bool(indexed)
        self.required = bool(required)

        self.default = default
        self.__value = self.value = None

        self.primary_key = primary_key
        self.read_only = read_only

    @property
    def obj(self):
        return self.__obj

    @obj.setter
    def obj(self, obj):
        if self.__obj is not None and obj is None:
            raise TypeError("Can't unbind Property")
        if obj is not None and not isinstance(obj, GraphObject):
            raise TypeError("Property can only be bound to Node "
                            "or Relationship.")
        self.__obj = obj

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


class GraphObject(object):
    pass


class NodeType(GraphObject):
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
