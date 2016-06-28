from collections import defaultdict

from neoalchemy.schema.base import NodeType


class Verb(object):
    def __init__(self, nodetype, param_id=None, **params):
        self.verb = self.__class__.__name__.upper()

        if isinstance(nodetype, self.__class__):
            self.nodetype = nodetype.nodetype
        else:
            self.nodetype = nodetype

        self.params = {}
        self._ = defaultdict(lambda: None)
        self._['param_id'] = param_id
        self._['relations'] = list(params.get('relations', []))
        self._compile_params(**params)

    def compile(self):
        self.query = '%s %s' % (self.verb, self._write_node())
        base_verb = self.__class__.__name__.upper()

        for i, relation in enumerate(self._['relations']):
            if relation.end_node is None:
                raise CompileError

            end_node = relation.end_node
            param_id = end_node._['param_id'] or (i + 1)
            end_node._.update(self._)
            end_node._['param_id'] = param_id
            end_node._compile_params(**end_node.params)
            self.params.update(end_node.params)

            end_node = end_node._write_node()
            if relation.type:
                self.query += '-[r%i:%s]->%s' % (i, relation.type, end_node)
            else:
                self.query += '-[r%i]->%s' % (i, end_node)

        if self._['where']:
            self.query += ' WHERE %s' % self._['where']

        if self._['return']:
            self.query += ' RETURN %s' % self._['return']
        elif self._['delete']:
            self.query += ' DELETE %s' % self._['delete']

        if self._['order_by']:
            self.query += ' ORDER BY %s' % self._['order_by']
        if self._['skip']:
            self.query += ' SKIP %i' % self._['skip']
        if self._['limit']:
            self.query += ' LIMIT %i' % self._['limit']

        return self

    def _compile_params(self, **params):
        param_id = self._['param_id']
        self.params = {}
        for prop_name, prop in self.nodetype.schema.items():
            param_key = '%s%s' % (prop_name,
                                  ('_%s' % param_id) if param_id else '')
            self.params[param_key] = params.get(prop_name, prop.default)
        return self

    def _parse_args(self, args):
        for param_id in args:
            nodevar = 'n' if param_id is None else 'n_%s' % param_id
            try:
                properties = args[param_id]
            except TypeError:
                yield nodevar
            else:
                for prop in properties:
                    yield '%s.%s' % (nodevar, prop)

    def _write_node(self):
        labels = ':'.join(self.nodetype.labels)

        properties = []
        if not self._['where']:
            for param_key in self.params:
                param_name = param_key.split('_')[0]
                properties.append('%s: {%s}' % (param_name, param_key))
        properties = ' {%s}' % ', '.join(properties) if properties else ''

        if self._['param_id']:
            node_key = 'n_%s' % self._['param_id']
        else:
            node_key = 'n'

        return '(%s:%s%s)' % (node_key, labels, properties)

    def return_(self, args=None, distinct=False):
        if not args:
            self._['return'] = '*'
            return self

        distinct = 'DISTINCT ' if distinct else ''
        self._['return'] = distinct + ', '.join(self._parse_args(args))
        return self

    def __call__(self, *args, **kw):
        if not self._['relations'] or self._['relations'][-1].end_node:
            self._['relations'].append(Relation(None))
        self._['relations'][-1].end_node = self.__class__(*args, **kw)
        return self

    def __getitem__(self, rel):
        self._['relations'].append(Relation(rel))
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

    def compile(self):
        if self.optional:
            self.verb = 'OPTIONAL MATCH'
        super(Match, self).compile()
        return self

    def delete(self, args, detach=False):
        detach = 'DETACH ' if detach else ''
        self._['delete'] = detach + ', '.join(self._parse_args(args))
        return self

    def limit(self, value):
        self._['limit'] = int(value)
        return self

    def order_by(self, args, desc=False):
        direction = 'DESC' if desc else 'ASC'
        self._['order_by'] = ' '.join((', '.join(self._parse_args(args)),
                                       direction))
        return self

    def skip(self, value):
        self._['skip'] = int(value)
        return self

    def where(self, cypher_conditional, param_id=None):
        if self._['where'] is None:
            self._['where'] = ''
        nodevar = 'n_%s' % param_id if param_id else 'n'
        self._['where'] += cypher_conditional % nodevar
        return self


class Merge(Verb):
    pass


class CompileError(SyntaxError):
    def __init__(self):
        super(CompileError, self).__init__('Cannot compile with '
                                           'incomplete relationships.')
