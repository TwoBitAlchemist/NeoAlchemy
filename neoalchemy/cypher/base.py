class CompileError(SyntaxError):
    def __init__(self):
        super(CompileError, self).__init__('Cannot compile with '
                                           'incomplete relationships.')


class Verb(object):
    def __init__(self, nodetype, param_id=None, **params):
        self.verb = self.__class__.__name__.upper()
        self.nodetype = nodetype
        self.param_id = param_id
        self.params = {}
        for prop in self.nodetype.schema:
            param_key = '%s%s' % (prop, ('_%s' % param_id) if param_id else '')
            self.params[param_key] = params.get(prop)
        self.relations = []

    def compile(self):
        labels = ':'.join(self.nodetype.labels)

        if self.params:
            properties = ' {%s}' % ', '.join('%(p)s: {%(p)s}' % {'p':p}
                                             for p in self.params)
        else:
            properties = ''

        if self.param_id:
            node_key = 'node_%s' % self.param_id
        else:
            node_key = 'node'

        self.query = '%s (%s:%s%s)' % (self.verb, node_key, labels, properties)

        for i, relation in enumerate(self.relations, start=1):
            if relation.end_node is None:
                raise CompileError

            end_node = self.__class__(relation.end_node, param_id=i)
            self.params.update(end_node.params)

            end_node = str(end_node).split(self.verb, 1)[1].lstrip()
            self.query += '-[:%s]->%s' % (relation.type, end_node)

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
    def __init__(self, *args, **kw):
        self.unique = bool(kw.pop('unique', None))
        super(Create, self).__init__(*args, **kw)

    def compile(self):
        if self.unique:
            self.verb = 'CREATE UNIQUE'
        return super(Create, self).compile()


class Match(Verb):
    def __init__(self, *args, **kw):
        self.optional = bool(kw.pop(optional))
        super(Match, self).__init__(*args, **kw)
        self.__limit = None
        self.__skip = None

    def compile(self):
        if self.optional:
            self.verb = 'OPTIONAL MATCH'
        super(Match, self).compile()
        if self.__skip:
            self.query += ' SKIP %i' % self.__skip
        if self.__limit:
            self.query += ' LIMIT %i' % self.__limit
        return self

    def limit(self, value):
        self.__limit = int(value)
        return self

    def skip(self, value):
        self.__skip = int(value)
        return self


class Merge(Verb):
    pass
