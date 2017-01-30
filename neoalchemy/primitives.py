import six

from .base import GraphObject, SetOnceDescriptor
from .cypher import Create, Match, Merge
from .exceptions import DetachedObjectError

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
        super(Node, self).__init__(**properties)
        if len(labels) == 1 and isinstance(labels[0], Node):
            self.labels = labels[0].labels
            self.type = labels[0].type
            self.var = labels[0].var
        else:
            if not labels:
                raise ValueError('Node must have at least one label.')
            self.labels = labels
            self.type = labels[-1]
            self.var = var

    def copy(self, shallow=False):
        if shallow:
            return Node(graph=self.graph, *self.labels)
        else:
            return Node(graph=self.graph, *self.labels,
                        **{key: prop.copy() for key, prop in self.items()})

    def pattern(self, inline_props=False):
        if inline_props and self.bound_keys:
            props = self.inline_properties
            return '(%s:`%s` %s)' % (self.var, '`:`'.join(self.labels), props)
        else:
            return '(%s:`%s`)' % (self.var, '`:`'.join(self.labels))

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
        return ExistsClause(self, exists)

    def pattern(self, inline_props=False):
        if self.start_node is None or self.end_node is None:
            raise DetachedObjectError(self)
        if (self.start_node is not self.end_node and
                self.start_node.var == self.end_node.var):
            raise ValueError("Relationship start node and end node cannot "
                             "employ the same Cypher variable.")

        base_pattern = '-[%s:`%s`%s%%s]-%s' % (self.var, self.type, self.depth,
                                               '>' if self.directed else '')
        if inline_props and self.bound_keys:
            pattern = base_pattern % (' ' + self.inline_properties)
        else:
            pattern = base_pattern % ''


        return '(%s)%s(%s)' % (self.start_node.var, pattern, self.end_node.var)
