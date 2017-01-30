from __future__ import unicode_literals

import six

from .base import CypherExpression, Property


class CypherQuery(list):
    def __init__(self, graph_obj, use_full_pattern=False):
        self.params = {}
        self.__extra_params = 0

        try:
            verb = self.verb
        except AttributeError:
            verb = self.__class__.__name__.upper()

        pattern = graph_obj.pattern(inline_props=use_full_pattern)
        super(CypherQuery, self).__init__(['%s %s' % (verb, pattern)])

    def delete(self, *args, **kw):
        detach = kw.get('detach')
        keyword = 'DETACH DELETE' if detach else 'DELETE'
        self.append(keyword + ', '.join(arg.var for arg in args))
        return self

    def limit(self, limit):
        self.append('LIMIT %i' % int(value))
        return self

    def order_by(self, *args):
        self.append('ORDER BY ' + ', '.join(arg.var for arg in args))
        return self

    def remove(self, *args):
        self.append('REMOVE ' + ', '.join(arg.var for arg in args))
        return self

    def return_(self, *args):
        if args:
            self.append('RETURN ' + ', '.join(arg.var for arg in args))
        else:
            self.append('RETURN *')
        return self

    def set(self, *props):
        prop_list = [self._add_expression(prop) for prop in props]
        if prop_list:
            self.append('    SET ' + ', '.join(prop_list))
        return self

    def skip(self, skip):
        self.append('SKIP %i' % int(value))
        return self

    def where(self, *exprs, **kw):
        or_ = kw.pop('or_', False)
        stmt_list = [self._add_expression(expr) for expr in exprs]
        if stmt_list:
            statements = ' AND '.join(stmt_list)
            if self[-1].startswith('    WHERE'):
                keyword = '      AND ' if not or_ else '       OR '
            else:
                keyword = '    WHERE '
            self.append(keyword + statements)
        return self

    def with_(self, *args):
        self.append('WITH ' + ', '.join(arg.var for arg in args))
        return self

    def set_param(self, name, value):
        if self.params.get(name) is not None:
            name = 'param%i' % self.__extra_params
            self.__extra_params += 1
        self.params[name] = value
        return name

    def _add_expression(self, expr):
        if isinstance(expr, Property):
            prop = expr
            expr = CypherExpression(prop, prop.value, '=')
        else:
            if not isinstance(expr, CypherExpression):
                raise ValueError('Must be CypherExpression or Property')

        expr.param = self.set_param(expr.param, expr.value)
        return str(expr)

    def __str__(self):
        return '\n'.join(map(str, self))

    def __and__(self, query):
        self.extend(query)
        return self

    def __or__(self, query):
        self.append('UNION ALL')
        self.extend(query)
        return self

    def __xor__(self, query):
        self.append('UNION')
        self.extend(query)
        return self


class Create(CypherQuery):
    def __init__(self, graph_obj):
        super(Create, self).__init__(graph_obj)
        self.set(*graph_obj.values())


class Match(CypherQuery):
    def __init__(self, graph_obj, optional=False):
        if optional:
            self.verb = 'OPTIONAL MATCH'
        super(Match, self).__init__(graph_obj)
        self.where(*(v for k, v in graph_obj.items()
                     if k in graph_obj.bound_keys))


class Merge(CypherQuery):
    def __init__(self, graph_obj):
        super(Merge, self).__init__(graph_obj, use_full_pattern=True)
        self.params.update({p.var: p.value for k, p in graph_obj.items()
                            if k in graph_obj.bound_keys})

    def on_create(self):
        self.append('ON CREATE')
        return self

    def on_match(self):
        self.append('ON MATCH')
        return self
