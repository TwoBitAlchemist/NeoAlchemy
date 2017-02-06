try:
    str = unicode
except NameError:
    pass


class QueryParams(dict):
    def __init__(self, *args, **kw):
        self.__extra_params = 0
        self.__last_key = None
        super(QueryParams, self).__init__(*args, **kw)

    @property
    def last_key(self):
        return self.__last_key

    def __setitem__(self, key, value):
        if self.get(key, object()) == value:
            return 
        if key is None or self.get(str(key)) is not None:
            key = 'param%i' % self.__extra_params
            self.__extra_params += 1
        self.__last_key = str(key)
        super(QueryParams, self).__setitem__(self.__last_key, value)

    def update(self, mapping):
        for key, value in mapping.items():
            self[key] = value


class CypherExpression(object):
    def __init__(self):
        self.__compiled = False
        self.__expr = self.__var = None
        self.params = QueryParams()

    def compile(self):
        self.__compiled = True
        return self

    def replace(self, old, new):
        self.__expr = self.__expr.replace(old, new)

    @property
    def expr(self):
        if self.__compiled:
            raise AttributeError("'%s' object has no attribute 'expr'" %
                                 self.__class__.__name__)
        return self.__expr

    @expr.setter
    def expr(self, value):
        if self.__compiled:
            raise AttributeError("Can't set attribute")
        self.__expr = value

    @property
    def var(self):
        if not self.__compiled: self.compile()
        return self.__var

    @var.setter
    def var(self, value):
        if self.__compiled:
            raise AttributeError("Can't set attribute")
        self.__var = value

    def __str__(self):
        if not self.__compiled: self.compile()
        return self.__expr

    def __bool__(self):
        return False


class CypherOperatorInterface(object):
    # Mathematical Operators
    def __add__(self, x):         # self + x
        return ComparisonExpression(self, x, '+')

    def __radd__(self, x):        # x + self
        return self.__add__(x)

    def __sub__(self, x):         # self - x
        return ComparisonExpression(self, x, '-')

    def __rsub__(self, x):        # x - self
        return ComparisonExpression(self, x, '-', reverse=True)

    def __mul__(self, x):         # self * x
        return ComparisonExpression(self, x, '*')

    def __rmul__(self, x):        # x * self
        return self.__mul__(x)

    def __div__(self, x):         # self / x
        return ComparisonExpression(self, x, '/')

    def __rdiv__(self, x):        # x / self
        return ComparisonExpression(self, x, '/', reverse=True)

    def __truediv__(self, x):     # self / x  (__future__.division)
        return self.__div__(x)

    def __rtruediv__(self, x):    # x / self  (__future__.division)
        return self.__rdiv__(x)

    def __floordiv__(self, x):    # self // x
        return self.__div__(x)

    def __rfloordiv__(self, x):   # x // self
        return self.__rdiv__(x)

    def __mod__(self, x):         # self % x
        return ComparisonExpression(self, x, '%')

    def __rmod__(self, x):        # x % self
        return ComparisonExpression(self, x, '%', reverse=True)

    def __pow__(self, x):         # self ** x
        return ComparisonExpression(self, x, '^')

    def __rpow__(self, x):        # x ** self
        return ComparisonExpression(self, x, '^', reverse=True)

    # Comparison Operators
    def __eq__(self, x):          # self == x
        if x is self: return True
        return ComparisonExpression(self, x, '=')

    def __ne__(self, x):          # self != x
        return ComparisonExpression(self, x, '<>')

    def __lt__(self, x):          # self < x
        return ComparisonExpression(self, x, '<')

    def __gt__(self, x):          # self > x
        return ComparisonExpression(self, x, '>')

    def __le__(self, x):          # self <= x
        return ComparisonExpression(self, x, '<=')

    def __ge__(self, x):          # self >= x
        return ComparisonExpression(self, x, '>=')


class ComparisonExpression(CypherExpression, CypherOperatorInterface):
    def __init__(self, left_operand, right_operand, operator, reverse=False):
        super(ComparisonExpression, self).__init__()
        self.__left_operand = left_operand
        self.__right_operand = right_operand
        self.__operator = operator
        self.__reverse = reverse

    def compile(self):
        if not isinstance(self.__right_operand, CypherOperatorInterface):
            if isinstance(self.__left_operand, ComparisonExpression):
                var = str(self.__left_operand)
                self.params.update(self.__left_operand.params)
            else:
                var = self.__left_operand.var

            if self.__right_operand is not None:
                value = self.__left_operand.type(self.__right_operand)
            else:
                value = None

            self.params[getattr(self.__left_operand, 'param', None)] = value
            self.var = var
            expr = (var, self.__operator, '{%s}' % self.params.last_key)
        else:
            expr = (self.__left_operand.var, self.__operator,
                    self.__right_operand.var)

        self.expr = ' '.join(reversed(expr) if self.__reverse else expr)
        super(ComparisonExpression, self).compile()
        return self

    def type(self, other):
        return other


class Exists(CypherExpression):
    def __init__(self, rel, exists=True):
        super(Exists, self).__init__()
        self.__exists = exists
        self.__rel = rel

    def compile(self):
        if self.__exists:
            self.expr = 'EXISTS(%s)'
        else:
            self.expr = 'NOT EXISTS(%s)'
        self.expr %= self.__rel.pattern()
        self.var = self.expr + ' AS %s_exists' % self.__rel.var
        super(Exists, self).compile()
        return self


class CypherFunction(object):
    def __init__(self, obj=None):
        if obj is None:
            self.__obj = None
        else:
            try:
                self.__obj, self.__var = obj.func, obj.inner_var
            except AttributeError:
                self.__obj = self.__var = obj.var

    @property
    def inner_var(self):
        return self.__var

    @property
    def func(self):
        if self.__obj is not None:
            return '%s(%s)' % (self.__class__.__name__.upper(), self.__obj)
        else:
            return '%s(*)' % self.__class__.__name__.upper()

    @property
    def var(self):
        return '%s AS %s_%s' % (self.func, self.inner_var,
                                self.__class__.__name__.lower())


class All(CypherFunction):
    pass


class Any(CypherFunction):
    pass


class Avg(CypherFunction):
    pass


class Collect(CypherFunction):
    pass


class Count(CypherFunction):
    pass


class Distinct(CypherFunction):
    pass


class Max(CypherFunction):
    pass


class Min(CypherFunction):
    pass


class None_(CypherFunction):
    pass


class Single(CypherFunction):
    pass


class Sum(CypherFunction):
    pass


class Unwind(CypherFunction):
    pass
