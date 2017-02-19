from weakref import WeakKeyDictionary

import six

from ..shared.objects import SetOnceDescriptor


class ManyToOneDescriptor(object):
    def __init__(self, name, relation):
        self.name = name
        self.relation = relation.copy()
        self.values = WeakKeyDictionary()

    def __get__(self, instance, owner):
        if instance is None:
            self.relation

        return self.values.get(instance)

    def __set__(self, instance, value):
        self.values[instance] = value

    def __delete__(self, instance):
        raise AttributeError("Can't remove attribute.")


class RelationMeta(type):
    def __init__(cls, class_name, bases, attrs):
        cls.type = SetOnceDescriptor('type', type=str)
        cls.backref = SetOnceDescriptor('backref', type=str)
        cls.obj = SetOnceDescriptor('obj')
        cls.restricted_types = SetOnceDescriptor('restricted_types',
                                                 type=tuple)
        for attr in ('unbound_start', 'unbound_end'):
            setattr(cls, attr, SetOnceDescriptor(attr, type=bool))
        super(RelationMeta, cls).__init__(class_name, bases, attrs)


@six.add_metaclass(RelationMeta)
class Relation(object):
    def __init__(self, type_, obj=None, backref=None,
                 restrict_types=(), **unbound_args):
        self.type = type_
        self.obj = obj
        self.backref = backref
        unbound = unbound_args['unbound'] = bool(unbound_args.get('unbound'))
        for arg in ('unbound_start', 'unbound_end'):
            unbound_args[arg] = bool(unbound_args.get(arg, unbound))
        self.__unbound_args = unbound_args
        self.restricted_types = restrict_types

    def copy(self, obj=None):
        return self.__class__(self.type, obj=obj or self.obj,
                              backref=self.backref,
                              restrict_types=self.restricted_types,
                              **dict(self.unbound_args))

    def add(self, related):
        if self.restricted_types:
            if not any(label in related.__node__.labels
                       for label in self.restricted_types):
                raise ValueError("Related object is '%r' but must be one of: "
                                 "'%s'" % (related,
                                           ', '.join(self.restricted_types)))
        return self.obj.add_relation(self.type, related, **self.__unbound_args)

    def drop(self, related):
        return self.obj.drop_relation(self.type, related, **self.__unbound_args)

    def match(self, *labels, **properties):
        return self.obj.get_relations(self.type, *labels, **properties)

    def create_backref(self, cls):
        raise NotImplementedError

    @property
    def unbound_args(self):
        return self.__unbound_args.items()


class OneToManyRelation(Relation):
    def __init__(self, type_, **kw):
        kw['unbound_start'] = kw['unbound'] = False
        super(OneToManyRelation, self).__init__(type_, **kw)

    def create_backref(self, cls):
        setattr(cls, self.backref, ManyToOneDescriptor(self.backref, self))


class ManyToManyRelation(Relation):
    def create_backref(self, cls):
        setattr(cls, self.backref, self.copy())
