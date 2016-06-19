from collections import OrderedDict


class Labeled(object):
    @property
    def label(self):
        return self.__label

    @label.setter
    def label(self, value):
        if self.__label is not None:
            raise ValueError("Cannot reset label on '%s' once "
                             "initialized." % self.__class__.__name__)
        self.__label = str(value).upper()


class Property(Labeled):
    def __init__(self, property_key):
        self.__key = str(property_key)


class NodeType(Labeled):
    def __init__(self, label, *properties):
        self.label = label
        schema = OrderedDict()
        for i, prop in enumerate(properties, start=1):
            if not isinstance(prop, Property):
                raise ValueError("Must be a Property object. "
                                 "'%s' given." % prop)
            if prop in schema:
                raise ValueError("Duplicate property found. Already defined "
                                 "at position %i." % schema[prop])

            schema[prop] = i
            prop.label = label

        self.__schema = tuple(schema.keys())

    @property
    def schema(self):
        return '\n'.join((repr(s) for s in self.__schema))


class Indexed(Property):
    def __repr__(self):
        return 'CREATE INDEX ON :%s(%s)' % (self.__label, self.__key)


class Unique(Property):
    def __repr__(self):
        return ('CREATE CONSTRAINT ON (node:%s) '
                'ASSERT node.%s IS UNIQUE' % (self.__label, self.__key))


class Required(Property):
    def __repr__(self):
        return ('CREATE CONSTRAINT ON (node:%s) '
                'ASSERT exists(node.%s)' % (self.__label, self.__key))
