from six import add_metaclass

from ..cypher import Create, Match
from .base import NodeType, Property


class PropertyDescriptor(object):
    def __init__(self, property_obj):
        self.__property = property_obj

    def __get__(self, obj, type=None):
        if obj is None:
            return self.__property
        return self.__property.value

    def __set__(self, obj, value):
        if obj is None:
            raise AttributeError("Can't set attribute.")

        if (self.__property.value is not None and
                self.__property.value != value):
            obj.__changed__[self.__property.name] = value
        self.__property.value = value

    def __delete__(self, obj):
        raise AttributeError("Can't remove attribute.")


class NodeMeta(type):
    def __new__(mcs, class_name, bases, attrs):
        if class_name != 'Node':
            labels = []
            properties = []
            for base in bases:
                try:
                    labels.extend(base.__nodetype__.labels)
                    properties.extend(base.__nodetype__.properties.values())
                except AttributeError:
                    pass
            labels.append(attrs.get('LABEL', class_name))

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
        for prop in self.__nodetype__.properties:
            setattr(self, prop, kw.get(prop))

    def create(self, unique=False):
        return self.graph.query(Create(self.__nodetype__, unique=unique),
                                **self.params)

    def match(self):
        match = Match(self.__nodetype__)
        for param, value in self.params.items():
            if value is None:
                continue
            param = getattr(self.__class__, param.rsplit('_', 1)[0])
            match = match.where(param==value)
        return list(self.graph.query(match.return_(), **self.params))[0]

    @property
    def params(self):
        return {'%s_n' % prop: getattr(self, prop)
                for prop in self.__nodetype__.properties}
