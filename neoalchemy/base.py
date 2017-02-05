from weakref import WeakKeyDictionary

import six

from .exceptions import ImmutableAttributeError
from .operations import CypherExpression, CypherOperatorInterface

try:
    str = unicode
except NameError:
    pass


class SetOnceDescriptor(object):
    def __init__(self, name, type=None):
        self.name = name
        self.type = type
        self.values = WeakKeyDictionary()

    def __get__(self, instance, owner):
        if instance is None:
            return getattr(owner, self.name)

        return self.values.get(instance)

    def __set__(self, instance, value):
        if self.values.get(instance) is not None:
            raise ImmutableAttributeError(self.name, instance)

        if self.type is not None and value is not None:
            self.values[instance] = self.type(value)
        else:
            self.values[instance] = value

    def __delete__(self, instance):
        raise ImmutableAttributeError(self.name, instance)


class GraphObject(object):
    def __init__(self, graph=None, **properties):
        # __properties must be set before anything else due to usage in
        # customized __getattr__/__setattr__ (see below)
        self.__properties = {}
        self.graph = graph

        for prop_name, prop in properties.items():
            if not isinstance(prop, Property):
                prop_val = prop
                prop = Property()
                prop.value = prop_val
            prop.name = prop_name
            prop.obj = self
            self.__properties[prop.name] = prop

        self.__primary_keys = None

    def bind(self, *keys):
        if len(keys) == 1 and keys[0] is None:
            self.__primary_keys = ()
        else:
            if any(key not in self.keys() for key in keys):
                raise ValueError('%s can only be bound to an existing '
                                 'property.' % self.__class__.__name__)
            if not keys:
                keys = [key for key, prop in self.items() if prop.primary_key]
            self.__primary_keys = tuple(keys)
        return self

    @property
    def bound_keys(self):
        return tuple(self.__primary_keys) if self.is_bound else ()

    @property
    def is_bound(self):
        return self.__primary_keys is not None

    @property
    def inline_properties(self):
        return '{%s}' % ', '.join('%s: {%s}' % (prop, self[prop].param)
                                                for prop in self.bound_keys)

    @property
    def properties(self):
        return dict(zip(self.keys(), (p.value for p in self.values())))

    def __getattr__(self, attr):
        if not attr.endswith('__properties') and attr in self.__properties:
            return self[attr].value
        else:
            return getattr(super(self.__class__, self), attr)

    def __setattr__(self, attr, value):
        if not attr.endswith('__properties') and attr in self.__properties:
            self[attr].value = value
        else:
            super(GraphObject, self).__setattr__(attr, value)

    def __getitem__(self, key):
        return self.__properties[key]

    def items(self):
        return self.__properties.items()

    def keys(self):
        return self.__properties.keys()

    def values(self):
        return self.__properties.values()

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, self.pattern())


class PropertyMeta(type):
    def __init__(cls, class_name, bases, attrs):
        cls.name = SetOnceDescriptor('name', type=str)
        cls.type = SetOnceDescriptor('type')
        cls.default = SetOnceDescriptor('default')
        cls.obj = SetOnceDescriptor('obj', type=PropertyMeta.valid_graph_obj)
        for attr in ('unique', 'indexed', 'required',
                     'primary_key', 'read_only'):
            setattr(cls, attr, SetOnceDescriptor(attr, type=bool))
        super(PropertyMeta, cls).__init__(class_name, bases, attrs)

    @staticmethod
    def valid_graph_obj(obj):
        if not isinstance(obj, GraphObject):
            raise ValueError('Property can only be bound to '
                             'Node or Relationship.')
        return obj


@six.add_metaclass(PropertyMeta)
class Property(CypherOperatorInterface):
    def __init__(self, obj=None, type=str, default=None, value=None,
                 indexed=False, unique=False, required=False,
                 primary_key=False, read_only=False):
        self.obj = obj
        self.type = type

        self.unique = bool(unique)
        self.indexed = self.unique or bool(indexed)
        self.required = bool(required)

        self.default = default
        self.__value = self.value = value

        self.primary_key = primary_key
        self.read_only = read_only

    def copy(self):
        copy = Property(type=self.type, default=self.default,
                        indexed=self.indexed, unique=self.unique,
                        required=self.required, primary_key=self.primary_key,
                        read_only=self.read_only)
        copy.value = self.value
        return copy

    @property
    def is_bound(self):
        return self.obj is not None

    @property
    def param(self):
        return self.__get_var('_')

    @property
    def schema(self):
        if not self.is_bound:
            raise TypeError('Cannot generate Cypher schema for '
                            'unbound Property.')

        params = {
            'label': self.obj.type,
            'lower_label': self.obj.type.lower(),
            'name': self.name,
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

    @property
    def var(self):
        return self.__get_var()

    def __get_var(self, separator='.'):
        if not self.is_bound:
            raise TypeError('Cannot create Cypher variable for '
                            'unbound Property.')

        return ''.join((self.obj.var, separator, self.name))

    def __repr__(self):
        return ('<Property(name=%s, type=%s, default=%r, value=%r)>' %
                (self.name, self.type, self.default, self.value))

    def __hash__(self):
        return id(self)
