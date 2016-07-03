from collections import defaultdict
import string

import six

from neoalchemy.schema.base import NodeType
from neoalchemy.schema.operations import (CypherExpressionList,
                                          LogicalCypherExpression)


class VerbCollection(list):
    def __and__(self, x):
        self.append(x)
        return self

    @property
    def params(self):
        params = {}
        for x in self:
            params.update(x.params)
        return params

    def __str__(self):
        return '\n'.join(map(str, self))


class Verb(object):
    def __init__(self, nodetype, param_id='n', **params):
        self.verb = self.__class__.__name__.upper()

        if isinstance(nodetype, self.__class__):
            self.nodetype = nodetype.nodetype
        else:
            self.nodetype = nodetype

        self._ = defaultdict(lambda: None)
        self._['params'] = {}
        self._['param_id'] = param_id
        self._['relations'] = list(params.get('relations', []))
        self._['set'] = CypherExpressionList()
        self._['where'] = CypherExpressionList()
        self._compile_params(**params)

    def compile(self):
        self.query = '%s %s' % (self.verb, self._write_node())
        base_verb = self.__class__.__name__.upper()

        for i, relation in enumerate(self._['relations'], start=1):
            if relation.end_node is None:
                raise CompileError

            end_node = relation.end_node
            param_id = end_node._['param_id']
            if param_id == 'n':
                param_id += str(i)
            end_node._.update(self._)
            end_node._['param_id'] = param_id
            end_node._compile_params(**end_node.params)
            self._['params'].update(end_node.params)

            end_node = end_node._write_node()
            if relation.type:
                self.query += '-[r%i:%s]->%s' % (i, relation.type, end_node)
            else:
                self.query += '-[r%i]->%s' % (i, end_node)

        param_count = 0
        if self._['where']:
            for expr in self._['where']:
                if not isinstance(expr, str):
                    if expr.node_key is None:
                        expr.node_key = self._['param_id']
                    if expr.param_key is None:
                        expr.param_key = 'param%i' % param_count
                        param_count += 1
                    self._['params'][expr.param_key] = expr.value
            self.query += ' WHERE %s' % self._['where']

        if self._['set']:
            for expr in self._['set']:
                if expr.node_key is None:
                    expr.node_key = self._['param_id']
                if expr.param_key is None:
                    expr.param_key = 'param%i' % param_count
                    param_count += 1
                self._['params'][expr.param_key] = expr.value
            self.query += ' SET %s' % ', '.join(map(str, self._['set']))

        if self._['remove']:
            self.query += ' REMOVE %s' % self._['remove']
        if self._['delete']:
            self.query += ' DELETE %s' % self._['delete']

        if self._['return']:
            self.query += ' RETURN %s' % self._['return']

        if self._['order_by']:
            self.query += ' ORDER BY %s' % self._['order_by']
        if self._['skip']:
            self.query += ' SKIP %i' % self._['skip']
        if self._['limit']:
            self.query += ' LIMIT %i' % self._['limit']

        return self

    def _compile_params(self, **params):
        param_id = self._['param_id']
        self._['params'] = {}
        for prop_name, prop in self.nodetype.schema.items():
            param_key = '%s%s' % (prop_name,
                                  ('_%s' % param_id) if param_id else '')
            self._['params'][param_key] = params.get(prop_name, prop.default)
        return self

    def _parse_args(self, args):
        if isinstance(args, six.string_types):
            yield args
            return
        for param_id in args:
            nodevar = param_id or 'n'
            try:
                properties = args[param_id]
            except TypeError:
                yield nodevar
            else:
                if isinstance(properties, six.string_types):
                    yield '%s.%s' % (nodevar, properties)
                else:
                    for prop in properties:
                        yield '%s.%s' % (nodevar, prop)

    def _write_node(self):
        labels = ':'.join(self.nodetype.labels)

        properties = []
        if not (self._['where'] or self._['set']):
            for param_key in self._['params']:
                param_name = '_'.join(param_key.split('_')[:-1]) or param_key
                properties.append('%s: {%s}' % (param_name, param_key))
        properties = ' {%s}' % ', '.join(properties) if properties else ''

        return '(%s:%s%s)' % (self._['param_id'], labels, properties)

    def remove(self, args=()):
        self._['remove'] = ', '.join(self._parse_args(args))
        return self

    def return_(self, args=None, distinct=False):
        if not args:
            self._['return'] = '*'
            return self

        distinct = 'DISTINCT ' if distinct else ''
        self._['return'] = distinct + ', '.join(self._parse_args(args))
        return self

    def set(self, property_, value, param_id=None):
        expr = LogicalCypherExpression('=', value,
                                       property_name=property_.name)
        expr.param_id = param_id
        self._['set'] += expr
        return self

    def where(self, expr, param_id=None, or_=False):
        expr.param_id = param_id
        if not self._['where']:
            self._['where'] += expr
            return self

        if or_:
            self._['where'] |= expr
        else:
            self._['where'] &= expr

        return self

    def __and__(self, x):
        return VerbCollection([self]) & x

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

    @property
    def params(self):
        return self._['params']


class Merge(Create):
    pass


class Match(Verb):
    def __init__(self, *args, **kw):
        self.optional = bool(kw.pop('optional', None))
        super(Match, self).__init__(*args, **kw)

    def compile(self):
        if self.optional:
            self.verb = 'OPTIONAL MATCH'
        return super(Match, self).compile()

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

    @property
    def params(self):
        return {key: value
                for key, value in dict(self._['params'] or {}).items()
                if value is not None}

    def skip(self, value):
        self._['skip'] = int(value)
        return self


class CompileError(SyntaxError):
    def __init__(self):
        super(CompileError, self).__init__('Cannot compile with '
                                           'incomplete relationships.')
