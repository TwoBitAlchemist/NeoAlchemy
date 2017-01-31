from six import add_metaclass

from .base import Property
from .cypher import Create, Match
from .primitives import Node


class PropertyDescriptor(object):
    def __init__(self, prop_name):
        self.name = prop_name

    def __get__(self, instance, owner):
        if instance is None:
            return owner.__node__[self.name]
        return instance.__node__[self.name].value

    def __set__(self, instance, value):
        prop = instance.__node__[self.name]
        if (prop.value is not None and prop.value != value):
            obj.__changed__[self.name] = value
        prop.value = value

    def __delete__(self, instance):
        raise AttributeError("Can't remove attribute.")


class OGMMeta(type):
    def __new__(mcs, class_name, bases, attrs):
        labels = []
        properties = {}
        for base in bases:
            try:
                labels.extend(base.__node__.labels)
                properties.update({key: prop.copy()
                                   for key, prop in base.__node__.items()})
            except AttributeError:
                continue

        if not attrs.get('__abstract__'):
            labels.append(attrs.get('LABEL') or class_name)

        properties.update({k: v for k, v in attrs.items()
                           if isinstance(v, Property)})
        for prop_name in properties:
            attrs[prop_name] = PropertyDescriptor(prop_name)
        attrs['__node__'] = Node(*labels, **properties)

        if attrs.get('graph') is not None:
            attrs['graph'].schema.add(attrs['__node__'])
            attrs['__node__'].graph = attrs['graph']

        return super(OGMMeta, mcs).__new__(mcs, class_name, bases, attrs)


@add_metaclass(OGMMeta)
class OGMBase(object):
    def __init__(self, **properties):
        self.__changed__ = {}
        for prop_name, value in properties.items():
            setattr(self, prop_name, value)
