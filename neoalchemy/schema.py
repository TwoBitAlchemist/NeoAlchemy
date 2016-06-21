from collections import OrderedDict


class Labeled(object):
    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, value):
        if getattr(self, '_label', None):
            raise AttributeError("Cannot reset label on '%s' once "
                                 "initialized." % self.__class__.__name__)
        self._label = str(value)

    def __str__(self):
        try:
            return self.schema
        except AttributeError:
            return super().__str__()


class Property(Labeled):
    def __init__(self, property_key,
                 indexed=False, unique=False, required=False):
        self._key = str(property_key)
        self.unique = bool(unique)
        self.indexed = self.unique or bool(indexed)
        self.required = bool(required)

    @property
    def schema(self):
        label, key = self.label, self._key
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

    def __hash__(self):
        return hash('::'.join((self.label, self._key)))

    def __eq__(self, other):
        try:
            return hash(self) == hash(other)
        except TypeError:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)


class NodeType(Labeled):
    def __init__(self, label, *properties):
        self.label = label
        self._schema = OrderedDict()
        for prop in properties:
            if not isinstance(prop, Property):
                raise TypeError("Must be a Property object. "
                                "'%s' given." % prop.__class__)
            prop.label = label
            if prop._key in self._schema:
                raise ValueError("Duplicate property found: '%s'" % prop._key)

            self._schema[prop._key] = prop

    @property
    def schema(self):
        return '\n'.join(filter(bool, map(str, self._schema.values())))

    def __getattribute__(self, name):
        schema = object.__getattribute__(self, '_schema')
        try:
            return schema[name]
        except KeyError:
            return object.__getattribute__(self, name)
