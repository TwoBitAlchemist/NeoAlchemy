

class Relation(object):
    def __init__(self, type, start_node=None, end_node=None):
        if isinstance(type, self.__class__):
            rel = type
            self.start_node = rel.start_node
            self.type = rel.type
            self.end_node = rel.end_node
        else:
            self.start_node = start_node
            self.type = type
            self.end_node = end_node


class Create(object):
    def __init__(self, nodetype, unique=False, relations=(), param_id=0,
                 **params):
        self.nodetype = nodetype
        self.unique = bool(unique)
        self.param_id = param_id
        self.params = {'%s%s' % (prop, param_id or ''): params.get(prop)
                       for prop in self.nodetype.schema}
        self.relations = list(relations)

    def compile(self):
        unique = 'UNIQUE ' if self.unique else ''
        labels = ':'.join(self.nodetype.labels)
        properties = ', '.join('%(p)s: {%(p)s}' % {'p': p}
                               for p in self.params)
        self.query = 'CREATE %s(node:%s {%s})' % (unique, labels, properties)

        if self.param_id:
            self.query = self.query.replace('node', 'node%s' % self.param_id)
        for i, relation in enumerate(self.relations, start=1):
            if relation.end_node is not None:
                end_node = self.__class__(relation.end_node, param_id=i)
                self.params.update(end_node.params)
            else:
                end_node = ''
            rel = '-[:%s]->%s' % (relation.type, str(end_node)[7:])
            self.query += rel

        return self

    def __call__(self, end_node):
        self.relations[-1].end_node = end_node
        return self

    def __getitem__(self, rel_type):
        self.relations.append(Relation(rel_type))
        return self

    def __str__(self):
        return self.compile().query
