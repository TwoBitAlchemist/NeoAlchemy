from collections import OrderedDict

from six import add_metaclass

from ..cypher import Create
from .operations import OperatorInterface


class Property(OperatorInterface):
    def __init__(self, property_key=None, type=str,
                 indexed=False, unique=False, required=False):
        self.__key = str(property_key) if property_key is not None else None
        self.unique = bool(unique)
        self.indexed = self.unique or bool(indexed)
        self.required = bool(required)
        self.type = type

    @property
    def key(self):
        return self.__key

    @key.setter
    def key(self, value):
        if self.__key is not None:
            raise AttributeError("Can't change key on %s "
                                 "once set." % self.__class__.__name__)
        self.__key = str(value)

    def __str__(self):
        label, key = self.label, self.__key
        schema = []
        if self.unique:
            schema.append('CREATE CONSTRAINT ON (node:%s) '
                          'ASSERT node.%s IS UNIQUE' % (label, key))
        elif self.indexed:
            schema.append('CREATE INDEX ON :%s(%s)' % (label, key))

        if self.required:
            schema.append('CREATE CONSTRAINT ON (node:%s) '
                          'ASSERT exists(node.%s)' % (label, key))
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
            if prop.key in self.__schema:
                raise ValueError("Duplicate property found: '%s'" % prop.key)

            self.__schema[prop.key] = prop

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

    def __hash__(self):
        return hash('::'.join(self.__labels))

    def __eq__(self, other):
        try:
            return hash(self) == hash(other)
        except TypeError:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return '\n'.join(filter(bool, map(str, self.__schema.values())))


class PropertyDescriptor(object):
    def __init__(self, property_obj):
        self.__property = property_obj
        self.__property.value = None

    def __get__(self, obj, type=None):
        if obj is None:
            return self.__property
        return self.__property.value

    def __set__(self, obj, value):
        if obj is None:
            raise AttributeError("Can't set attribute.")

        value = self.__property.type(value)
        if (self.__property.value is not None and
                self.__property.value != value):
            obj.__changed__[self.__property.key] = value
        self.__property.value = value

    def __delete__(self, obj):
        raise AttributeError("Can't remove attribute.")


class NodeMeta(type):
    def __new__(mcs, class_name, bases, attrs):
        labels = [attrs.get('LABEL', class_name)]
        for base in bases:
            try:
                labels.append(base.LABEL)
            except AttributeError:
                pass

        properties = []
        for prop_name, prop in attrs.items():
            if isinstance(prop, Property):
                if prop.key is None:
                    prop.key = prop_name
                properties.append(prop)
                attrs[prop_name] = PropertyDescriptor(prop)

        attrs['__nodetype__'] = NodeType(labels[0], *properties,
                                         extra_labels=labels[1:])

        if attrs.get('graph') is not None:
            attrs['graph'].schema.add(attrs['__nodetype__'])

        return super(NodeMeta, mcs).__new__(mcs, class_name, bases, attrs)


@add_metaclass(NodeMeta)
class Node(object):
    def __init__(self, **kw):
        self.__changed__ = {}
        for prop in self.__nodetype__.schema:
            setattr(self, prop, kw.get(prop))

    def create(self):
        params = {prop: getattr(self, prop)
                  for prop in self.__nodetype__.schema}
        return self.graph.query(Create(self.__nodetype__, **params))
