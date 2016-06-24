

class Verb(object):
    def __init__(self, nodetype, relations=(), param_id=0,
                 **params):
        self.verb = self.__class__.__name__.upper()
        self.nodetype = nodetype
        self.param_id = param_id
        self.params = {'%s%s' % (prop, param_id or ''): params.get(prop)
                       for prop in self.nodetype.schema}
        self.relations = list(relations)

    def compile(self):
        labels = ':'.join(self.nodetype.labels)
        properties = ', '.join('%(p)s: {%(p)s}' % {'p':p} for p in self.params)
        self.query = '%s (node:%s {%s})' % (self.verb, labels, properties)
        if self.param_id:
            self.query = self.query.replace('node', 'node%s' % self.param_id)
        for i, relation in enumerate(self.relations, start=1):
            if relation.end_node is not None:
                end_node = self.__class__(relation.end_node, param_id=i)
                self.params.update(end_node.params)
            else:
                end_node = ''

            end_node = str(end_node).split(self.verb, 1)[1].lstrip()
            rel = '-[:%s]->%s' % (relation.type, end_node)
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


class Create(Verb):
    def __init__(self, *args, unique=False, **kw):
        self.unique = bool(unique)
        super(Create, self).__init__(*args, **kw)

    def compile(self):
        if self.unique:
            self.verb += ' UNIQUE'
        return super(Create, self).compile()


class Match(Verb):
    pass


class Merge(Verb):
    pass
