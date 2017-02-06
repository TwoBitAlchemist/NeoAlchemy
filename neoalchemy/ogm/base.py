from six import add_metaclass

from ..cypher import Create, Match
from ..primitives import Node
from ..exceptions import DetachedObjectError, UnboundedWriteOperation
from ..shared.objects import Property


class PropertyDescriptor(object):
    def __init__(self, prop_name):
        self.name = prop_name

    def __get__(self, instance, owner):
        if instance is None:
            return owner.__node__[self.name]
        return instance.__node__[self.name].value

    def __set__(self, instance, value):
        prop = instance.__node__[self.name]
        if prop.value != value:
            instance.__changed__[self.name] = (prop.value, value)
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
            self.__node__[prop_name].value = value

    def bind(self, *keys):
        self.__node__.bind(*keys)

    @property
    def bound_keys(self):
        return self.__node__.bound_keys

    @property
    def is_bound(self):
        return self.__node__.is_bound

    def create(self):
        if self.graph is None:
            raise DetachedObjectError(self, action='create')

        create = Create(self.__node__)
        self.graph.run(str(create), **create.params)
        return self

    def delete(self, detach=True, force=False):
        if self.graph is None:
            raise DetachedObjectError(self, action='delete')
        if not self.is_bound:
            self.bind()
            if not self.bound_keys and not force:
                extra_info = 'Use delete_all() or delete(force=True)'
                raise UnboundedWriteOperation(self, extra_info)

        match = Match(self.__node__).delete(self.__node__, detach=detach)
        self.graph.run(str(match), **match.params)

    def delete_all(self):
        self.bind(None)
        self.delete(detach=True, force=True)

    @classmethod
    def match(self, **properties):
        if self.graph is None:
            raise DetachedObjectError(self, action='match')

        matched = self.__node__.copy(**properties)
        match = Match(matched).return_(matched)
        return self.graph.run(str(match), **match.params)

    def merge(self, singleton=False):
        if self.graph is None:
            raise DetachedObjectError(self, action='merge')
        if not self.is_bound:
            self.bind()
            if not self.bound_keys and not singleton:
                extra_info = 'To merge a singleton pass singleton=True.'
                raise UnboundedWriteOperation(self, extra_info)

        merge = (
            Merge(self.__node__)
                .on_create()
                    .set(*self.__node__.values())
                .on_match()
                    .set(*(self.__node__[key] for key in self.__changed__))
            .return_(self.__node__)
        )
        return self.graph.run(str(merge), **merge.params)
