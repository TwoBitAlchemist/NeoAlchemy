

class Create(object):
    def __init__(self, *labels, unique=False, **properties):
        self.labels = labels
        self.properties = properties
        self.unique = unique

    def __repr__(self):
        unique = 'UNIQUE ' if self.unique else ''
        labels = ':%s' % ':'.join(self.labels) if self.labels else ''
        properties = (' {%s}' % ', '.join(': '.join((k, self.__repr_val(v)))
                                          for k, v in self.properties.items())
                      if self.properties else '')
        return 'CREATE %s(node%s%s)' % (unique, labels, properties)

    def __repr_val(self, value):
        if isinstance(value, str):
            return '"%s"' % value
