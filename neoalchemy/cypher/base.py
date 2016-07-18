from collections import defaultdict
import string

import six

from neoalchemy.schema.base import NodeType
from neoalchemy.schema.operations import (CypherExpressionList,
                                          LogicalCypherExpression)


class VerbCollection(list):
    def __init__(self, *args, **kw):
        super(VerbCollection, self).__init__(*args, **kw)
        for x in self:
            x._['return'] = None

    def __and__(self, x):
        self.append(x)
        return self

    def __or__(self, x):
        self.extend(['UNION ALL', x])
        return self

    def __xor__(self, x):
        self.extend(['UNION', x])
        return self

    @property
    def params(self):
        params = {}
        for x in self:
            params.update(x.params)
        return params

    def __str__(self):
        return '\n'.join(map(str, self))

    def delete(self, *args, **kw):
        self[-1].delete(*args, **kw)
        return self

    def remove(self, *args, **kw):
        self[-1].remove(*args, **kw)
        return self

    def return_(self, *args, **kw):
        self[-1].return_(*args, **kw)
        return self


class CypherVerb(object):
    def __init__(self, nodetype, var='n', **params):
        self.verb = self.__class__.__name__.upper()

        try:
            self.nodetype = nodetype.nodetype
        except AttributeError:
            try:
                self.nodetype = nodetype.__nodetype__
            except AttributeError:
                self.nodetype = nodetype

        self._ = defaultdict(lambda: None)
        self.params = {}
        self._['relations'] = list(params.get('relations', []))
        self._['set'] = CypherExpressionList()
        self._['where'] = CypherExpressionList()
        self._['var'] = var
        self._compile_params(**params)

    def compile(self):
        self.query = '%s %s' % (self.verb, self._write_node())
        base_verb = self.__class__.__name__.upper()

        for i, relation in enumerate(self._['relations'], start=1):
            if relation.end_node is None:
                raise CompileError

            end_node = relation.end_node
            var = end_node._['var']
            if var == 'n':
                var += str(i)
            end_node._.update(self._)
            end_node._['var'] = var
            end_node._compile_params(**end_node.params)
            self.params.update(end_node.params)

            end_node = end_node._write_node()
            if relation.type:
                self.query += '-[r%i:%s]->%s' % (i, relation.type, end_node)
            else:
                self.query += '-[r%i]->%s' % (i, end_node)

        param_count = 0
        if self._['where']:
            for expr in self._['where']:
                if not isinstance(expr, six.string_types):
                    if expr.node_key is None:
                        expr.node_key = self._['var']
                    if expr.param_key is None:
                        expr.param_key = 'param%i' % param_count
                        param_count += 1
                    self.params[expr.param_key] = expr.value
            self.query += ' WHERE %s' % self._['where']

        if self._['set']:
            for expr in self._['set']:
                if expr.node_key is None:
                    expr.node_key = self._['var']
                if expr.param_key is None:
                    expr.param_key = 'param%i' % param_count
                    param_count += 1
                self.params[expr.param_key] = expr.value
            self.query += ' SET %s' % ', '.join(map(str, self._['set']))

        if self._['remove']:
            self.query += '\nREMOVE %s' % self._['remove']
        if self._['delete']:
            self.query += '\nDELETE %s' % self._['delete']

        if self._['return']:
            self.query += '\nRETURN %s' % self._['return']

        if self._['order_by']:
            self.query += ' ORDER BY %s' % self._['order_by']
        if self._['skip']:
            self.query += ' SKIP %i' % self._['skip']
        if self._['limit']:
            self.query += ' LIMIT %i' % self._['limit']

        return self

    def _compile_params(self, **params):
        var = self._['var']
        self.params = {}
        for prop_name, prop in self.nodetype.properties.items():
            param_key = '%s%s' % (prop_name, ('_%s' % var) if var else '')
            self.params[param_key] = params.get(prop_name, prop.value)
        return self

    def _parse_args(self, args):
        if isinstance(args, six.string_types):
            yield args
            return
        for var in args:
            nodevar = var or 'n'
            try:
                properties = args[var]
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
            for param_key in self.params:
                param_name = '_'.join(param_key.split('_')[:-1]) or param_key
                properties.append('%s: {%s}' % (param_name, param_key))
        properties = ' {%s}' % ', '.join(properties) if properties else ''

        return '(%s:%s%s)' % (self._['var'], labels, properties)

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

    def set(self, var=None, **params):
        for prop_name, value in params.items():
            try:
                property_ = self.nodetype.properties[prop_name]
            except KeyError:
                continue
            expr = LogicalCypherExpression('=', value, property_)
            expr.node_key = var
            self._['set'] += expr
        return self

    def skip(self, value):
        self._['skip'] = int(value)
        return self

    def where(self, expr, var=None, or_=False):
        expr.node_key = var
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

    def __or__(self, x):
        return VerbCollection([self]) | x

    def __xor__(self, x):
        return VerbCollection([self]) ^ x

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


class Create(CypherVerb):
    def __init__(self, *args, **kw):
        self.unique = bool(kw.pop('unique', None))
        super(Create, self).__init__(*args, **kw)

    def compile(self):
        if self.unique:
            self.verb = 'CREATE UNIQUE'
        return super(Create, self).compile()


class Merge(Create):
    pass


class Match(CypherVerb):
    def __init__(self, *args, **kw):
        self.optional = bool(kw.pop('optional', None))
        super(Match, self).__init__(*args, **kw)

    def compile(self):
        if self.optional:
            self.verb = 'OPTIONAL MATCH'
        return super(Match, self).compile()


class CompileError(SyntaxError):
    def __init__(self):
        super(CompileError, self).__init__('Cannot compile with '
                                           'incomplete relationships.')
