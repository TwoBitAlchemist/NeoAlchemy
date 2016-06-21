from collections import OrderedDict


class Property(object):
    def __init__(self, property_key,
                 indexed=False, unique=False, required=False):
        self.__key = str(property_key)
        self.unique = bool(unique)
        self.indexed = self.unique or bool(indexed)
        self.required = bool(required)

    @property
    def key(self):
        return self.__key

    def __hash__(self):
        return hash('::'.join((self.label, self.__key)))

    def __eq__(self, other):
        try:
            return hash(self) == hash(other)
        except TypeError:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

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
    def __init__(self, label, *properties):
        self.__label = label
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
    def label(self):
        return self.__label

    def __getattr__(self, attr):
        try:
            return self.__schema[attr]
        except KeyError:
            super().__getattribute__(attr)

    def __str__(self):
        return '\n'.join(filter(bool, map(str, self.__schema.values())))
