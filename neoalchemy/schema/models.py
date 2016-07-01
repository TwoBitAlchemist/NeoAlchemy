from six import add_metaclass

from ..cypher import Create
from .base import NodeType, Property


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
            obj.__changed__[self.__property.name] = value
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
                if prop.name is None:
                    prop.name = prop_name
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
