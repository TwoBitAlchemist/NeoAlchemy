

class Create(object):
    def __init__(self, nodetype, unique=False, **params):
        self.nodetype = nodetype
        self.unique = bool(unique)
        self.params = {prop: params.get(prop) for prop in self.nodetype.schema}

    def __str__(self):
        unique = 'UNIQUE ' if self.unique else ''
        labels = ':'.join(self.nodetype.labels)
        properties = ('%(p)s: {%(p)s}' % {'p': p} for p in self.params)

        return 'CREATE %s(node:%s {%s})' % (unique, labels,
                                            ', '.join(properties))
