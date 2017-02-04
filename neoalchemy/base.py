from weakref import WeakKeyDictionary

import six

from .exceptions import ImmutableAttributeError

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
            return self[attr]
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


def _valid_graph_obj(obj):
    if not isinstance(obj, GraphObject):
        raise ValueError('Property can only be bound to Node or Relationship.')
    return obj


class CypherExpression(object):
    def __init__(self, property_, operand, operator, reverse=False):
        if not isinstance(property_, Property):
            raise ValueError('CypherExpression must be instantiated with '
                             'Property as first argument.')
        self.__property_ = property_
        self.__operand = operand
        self.__operator = operator
        self.__reverse = reverse
        self.__compiled = False

    def compile(self):
        if not isinstance(self.__operand, Property):
            self.__param = self.__property_.param
            self.__var = self.__property_.var
            if self.__operand is not None:
                self.__value = self.__property_.type(self.__operand)
            else:
                self.__value = None
            expr = (self.__property_.var, self.__operator,
                    '{%s}' % self.__property_.param)
        else:
            self.__param = self.__value = self.__var = None
            expr = (self.__property_.var, self.__operator, self.__operand.var)

        self.__expr = ' '.join(reversed(expr) if self.__reverse else expr)
        self.__compiled = True

    @property
    def param(self):
        if not self.__compiled: self.compile()
        return self.__param

    @param.setter
    def param(self, value):
        if not self.__compiled: self.compile()
        if self.__param is None:
            return
        if value is None:
            raise AttributeError("Can't unset parameter")

        self.__expr = self.__expr.replace(self.__param, value)
        self.__param = value

    @property
    def var(self):
        if not self.__compiled: self.compile()
        return self.__var

    @property
    def value(self):
        if not self.__compiled: self.compile()
        return self.__value

    def __str__(self):
        if not self.__compiled: self.compile()
        return self.__expr

    def __bool__(self):
        return False


class PropertyMeta(type):
    def __init__(cls, class_name, bases, attrs):
        cls.name = SetOnceDescriptor('name', type=str)
        cls.type = SetOnceDescriptor('type')
        cls.default = SetOnceDescriptor('default')
        cls.obj = SetOnceDescriptor('obj', type=_valid_graph_obj)
        for attr in ('unique', 'indexed', 'required',
                     'primary_key', 'read_only'):
            setattr(cls, attr, SetOnceDescriptor(attr, type=bool))
        super(PropertyMeta, cls).__init__(class_name, bases, attrs)


@six.add_metaclass(PropertyMeta)
class Property(object):
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

    # Mathematical Operators
    def __add__(self, x):         # self + x
        return CypherExpression(self, x, '+')

    def __radd__(self, x):        # x + self
        return self.__add__(x)

    def __sub__(self, x):         # self - x
        return CypherExpression(self, x, '-')

    def __rsub__(self, x):        # x - self
        return CypherExpression(self, x, '-', reverse=True)

    def __mul__(self, x):         # self * x
        return CypherExpression(self, x, '*')

    def __rmul__(self, x):        # x * self
        return self.__mul__(x)

    def __div__(self, x):         # self / x
        return CypherExpression(self, x, '/')

    def __rdiv__(self, x):        # x / self
        return CypherExpression(self, x, '/', reverse=True)

    def __truediv__(self, x):     # self / x  (__future__.division)
        return self.__div__(x)

    def __rtruediv__(self, x):    # x / self  (__future__.division)
        return self.__rdiv__(x)

    def __floordiv__(self, x):    # self // x
        return self.__div__(x)

    def __rfloordiv__(self, x):   # x // self
        return self.__rdiv__(x)

    def __mod__(self, x):         # self % x
        return CypherExpression(self, x, '%')

    def __rmod__(self, x):        # x % self
        return CypherExpression(self, x, '%', reverse=True)

    def __pow__(self, x):         # self ** x
        return CypherExpression(self, x, '^')

    def __rpow__(self, x):        # x ** self
        return CypherExpression(self, x, '^', reverse=True)

    # Comparison Operators
    def __eq__(self, x):          # self == x
        if x is self: return True
        return CypherExpression(self, x, '=')

    def __ne__(self, x):          # self != x
        return CypherExpression(self, x, '<>')

    def __lt__(self, x):          # self < x
        return CypherExpression(self, x, '<')

    def __gt__(self, x):          # self > x
        return CypherExpression(self, x, '>')

    def __le__(self, x):          # self <= x
        return CypherExpression(self, x, '<=')

    def __ge__(self, x):          # self >= x
        return CypherExpression(self, x, '>=')
