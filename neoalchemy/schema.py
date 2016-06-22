from collections import OrderedDict


class Property(object):
    def __init__(self, property_key=None,
                 indexed=False, unique=False, required=False):
        self.__key = str(property_key) if property_key is not None else None
        self.unique = bool(unique)
        self.indexed = self.unique or bool(indexed)
        self.required = bool(required)

    @property
    def key(self):
        return self.__key

    @key.setter
    def key(self, value):
        if self.__key is not None:
            raise AttributeError("Can't change key on %s "
                                 "once set." % self.__class__.__name__)
        self.__key = value

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

    @property
    def schema(self):
        return self.__schema

    def __getattr__(self, attr):
        try:
            return self.__schema[attr]
        except KeyError:
            super().__getattribute__(attr)

    def __str__(self):
        return '\n'.join(filter(bool, map(str, self.__schema.values())))


class Node(type):
    def __new__(metaclass, class_name, bases, attrs):
        attrs['LABEL'] = attrs.get('LABEL', class_name)

        def properties():
            for attr_name, attr in attrs.items():
                if isinstance(attr, Property):
                    if attr.key is None:
                        attr.key = attr_name
                    yield attr

        attrs['__nodetype__'] = NodeType(attrs['LABEL'], *properties())

        if attrs['graph'] is not None:
            attrs['graph'].schema.add(attrs['__nodetype__'])

        return super().__new__(metaclass, class_name, bases, attrs)
