import six

from .cypher import Create, Match, Merge, Exists
from .exceptions import DetachedObjectError
from .shared.objects import GraphObject, SetOnceDescriptor

try:
    str = unicode
except NameError:
    pass


class NodeMeta(type):
    def __init__(cls, class_name, bases, attrs):
        cls.labels = SetOnceDescriptor('labels', type=lambda x: tuple(set(x)))
        cls.type = SetOnceDescriptor('type', type=str)
        super(NodeMeta, cls).__init__(class_name, bases, attrs)


@six.add_metaclass(NodeMeta)
class Node(GraphObject):
    def __init__(self, *labels, **properties):
        var = properties.pop('var', 'node')
        if len(labels) == 1 and isinstance(labels[0], Node):
            node = labels[0]
            properties.update({key: prop.copy() for key, prop in node.items()})
        else:
            node = None
        super(Node, self).__init__(**properties)
        if node is not None:
            self.labels = node.labels
            self.type = node.type
            self.var = node.var
        else:
            self.labels = labels
            self.var = var
            try:
                self.type = labels[-1]
            except IndexError:
                self.type = None

    def copy(self, shallow=False, **properties):
        var = properties.pop('var', self.var)
        if shallow:
            copy = Node(self, graph=self.graph, var=var)
        else:
            copy = Node(self, graph=self.graph, var=var,
                        **{key: prop.copy() for key, prop in self.items()})
        if self.is_bound:
            copy.bind(*self.bound_keys)
        for key, value in properties.items():
            copy[key].value = value
        return copy

    @property
    def __node__(self):
        return self

    def pattern(self, inline_props=False):
        labels = ':`%s`' % '`:`'.join(self.labels) if self.labels else ''
        if inline_props and self.bound_keys:
            props = self.inline_properties
            return '(%s%s %s)' % (self.var, labels, props)
        else:
            return '(%s%s)' % (self.var, labels)

    @property
    def schema(self):
        return [stmt for prop in self.values() for stmt in prop.schema]


class RelationshipMeta(type):
    def __init__(cls, class_name, bases, attrs):
        cls.type = SetOnceDescriptor('type', type=str)
        cls.directed = SetOnceDescriptor('directed', type=bool)
        for attr in ('start_node', 'end_node'):
            setattr(cls, attr, SetOnceDescriptor(attr, type=Node))
        super(RelationshipMeta, cls).__init__(class_name, bases, attrs)


@six.add_metaclass(RelationshipMeta)
class Relationship(GraphObject):
    def __init__(self, type, start_node=None, end_node=None, depth=None,
                 directed=True, var='rel', **properties):
        super(Relationship, self).__init__(**properties)
        self.var = var
        self.type = type
        self.start_node = start_node
        self.end_node = end_node
        self.depth = depth
        self.directed = directed

    @property
    def depth(self):
        return self.__depth

    @depth.setter
    def depth(self, depth):
        if depth is None:
            self.__depth = ''
        elif depth == -1:
            self.__depth = '*'
        else:
            try:
                self.__depth = '%i' % int(depth)
            except ValueError:
                self.__depth = '%i..%i' % map(int, depth)

    def exists(self, exists=True):
        return Exists(self, exists)

    def pattern(self, inline_props=False):
        if self.start_node is None or self.end_node is None:
            raise DetachedObjectError(self)
        if (self.start_node is not self.end_node and
                self.start_node.var == self.end_node.var):
            raise ValueError("Relationship start node and end node cannot "
                             "employ the same Cypher variable.")

        type_spec = (':`%s`' % self.type) if self.type is not None else ''
        base_pattern = '-[%s%s%s%%s]-%s' % (self.var, type_spec, self.depth,
                                            '>' if self.directed else '')
        if inline_props and self.bound_keys:
            pattern = base_pattern % (' ' + self.inline_properties)
        else:
            pattern = base_pattern % ''


        return '(%s)%s(%s)' % (self.start_node.var, pattern, self.end_node.var)
