from neoalchemy.schema.base import NodeType


class Verb(object):
    def __init__(self, nodetype, param_id=None, **params):
        self.verb = self.__class__.__name__.upper()

        if isinstance(nodetype, self.__class__):
            self.nodetype = nodetype.nodetype
        else:
            self.nodetype = nodetype

        self.param_id = param_id
        self.params = {}
        for prop_name, prop in self.nodetype.schema.items():
            param_key = '%s%s' % (prop_name,
                                  ('_%s' % param_id) if param_id else '')
            self.params[param_key] = params.get(prop_name, prop.default)

        self.relations = []

    def compile(self):
        labels = ':'.join(self.nodetype.labels)

        properties = []
        for param_key in self.params:
            param_name = param_key.split('_')[0]
            properties.append('%s: {%s}' % (param_name, param_key))
        properties = (' {%s}' % ', '.join(properties)) if properties else ''

        if self.param_id:
            node_key = 'node_%s' % self.param_id
        else:
            node_key = 'node'

        self.query = '%s (%s:%s%s)' % (self.verb, node_key, labels, properties)
        base_verb = self.__class__.__name__.upper()

        for i, relation in enumerate(self.relations):
            if relation.end_node is None:
                raise CompileError

            if relation.end_node.param_id:
                end_node = relation.end_node
            else:
                end_node = self.__class__(relation.end_node, param_id=i+1)
            self.params.update(end_node.params)

            end_node = str(end_node).split(base_verb, 1)[1].lstrip()
            if relation.type:
                self.query += '-[r%i:%s]->%s' % (i, relation.type, end_node)
            else:
                self.query += '-[r%i]->%s' % (i, end_node)

        return self

    def __call__(self, *args, **kw):
        if not self.relations or self.relations[-1].end_node:
            self.relations.append(Relation(None))
        self.relations[-1].end_node = self.__class__(*args, **kw)
        return self

    def __getitem__(self, rel):
        self.relations.append(Relation(rel))
        return self

    def __str__(self):
        return self.compile().query


class Relation(NodeType):
    def __init__(self, type, start_node=None, end_node=None, *args, **kw):
        if isinstance(type, self.__class__):
            rel = type
            self.start_node = rel.start_node
            self.type = rel.type
            self.end_node = rel.end_node
        else:
            self.start_node = start_node
            self.type = type or ''
            self.end_node = end_node
        super(Relation, self).__init__(self.type, *args, **kw)


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
        self.optional = bool(kw.pop('optional', None))
        super(Match, self).__init__(*args, **kw)
        self.__limit = None
        self.__skip = None
        self.__where = ''

    def compile(self):
        if self.optional:
            self.verb = 'OPTIONAL MATCH'
        super(Match, self).compile()
        if self.__where:
            self.query += ' WHERE %s' % self.__where
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

    def where(self, cypher_conditional, param_id=''):
        self.__where += cypher_conditional % param_id
        return self


class Merge(Verb):
    pass


class CompileError(SyntaxError):
    def __init__(self):
        super(CompileError, self).__init__('Cannot compile with '
                                           'incomplete relationships.')
