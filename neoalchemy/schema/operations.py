

class CypherExpressionList(list):
    def __add__(self, x):
        if not isinstance(x, list):
            x = [x]
        self.extend(x)
        return self

    def __radd__(self, x):
        return self.__class__(x) + self

    def __iadd__(self, x):
        self.__add__(x)
        return self

    def __and__(self, x):
        self.extend(['AND', x])
        return self

    def __or__(self, x):
        self.extend(['OR', x])
        return self

    def __str__(self):
        return ' '.join(map(str, self))


class CypherExpression(object):
    def __init__(self, operator, value,
                 node_key=None, param_key=None, reverse=False):
        self.operator = operator
        self.value = value
        self.node_key = node_key
        self.param_name = self.param_key = param_key
        self.reverse = reverse
        self.param_id = None

    def compile(self):
        if self.param_id:
            self.param_key = '%s_%s' % (self.param_name, self.param_id)
        else:
            self.param_key = self.param_name
        return self

    def __and__(self, x):
        return CypherExpressionList([self, 'AND', x])

    def __or__(self, x):
        return CypherExpressionList([self, 'OR', x])

    def __str__(self):
        key = '.'.join(key for key in (self.node_key, self.param_name) if key)
        expr = [key, self.operator, '{%s}' % self.param_key]
        return ' '.join(expr if not self.reverse else reversed(expr))


class OperatorInterface(object):
    # Mathematical Operators
    def __add__(self, x):         # self + x
        return CypherExpression('+', x, param_key=self.key)

    def __radd__(self, x):        # x + self
        return self.__add__(x)

    def __sub__(self, x):         # self - x
        return CypherExpression('-', x, param_key=self.key)

    def __rsub__(self, x):        # x - self
        return CypherExpression('-', x, param_key=self.key, reverse=True)

    def __mul__(self, x):         # self * x
        return CypherExpression('*', x, param_key=self.key)

    def __rmul__(self, x):        # x * self
        return self.__mul__(x)

    def __div__(self, x):         # self / x
        return CypherExpression('/', x, param_key=self.key)

    def __rdiv__(self, x):        # x / self
        return CypherExpression('/', x, param_key=self.key, reverse=True)

    def __truediv__(self, x):     # self / x  (__future__.division)
        return self.__div__(x)

    def __rtruediv__(self, x):    # x / self  (__future__.division)
        return self.__rdiv__(x)

    def __floordiv__(self, x):    # self // x
        return self.__div__(x)

    def __rfloordiv__(self, x):   # x // self
        return self.__rdiv__(x)

    def __mod__(self, x):         # self % x
        return CypherExpression('%', x, param_key=self.key)

    def __rmod__(self, x):        # x % self
        return CypherExpression('%', x, param_key=self.key, reverse=True)

    def __pow__(self, x):         # self ** x
        return CypherExpression('^', x, param_key=self.key)

    def __rpow__(self, x):        # x ** self
        return CypherExpression('^', x, param_key=self.key, reverse=True)

    # Comparison Operators
    def __eq__(self, x):          # self == x
        return CypherExpression('=', x, param_key=self.key)

    def __ne__(self, x):          # self != x
        return CypherExpression('<>', x, param_key=self.key)

    def __lt__(self, x):          # self < x
        return CypherExpression('<', x, param_key=self.key)

    def __gt__(self, x):          # self > x
        return CypherExpression('>', x, param_key=self.key)

    def __le__(self, x):          # self <= x
        return CypherExpression('<=', x, param_key=self.key)

    def __ge__(self, x):          # self >= x
        return CypherExpression('>=', x, param_key=self.key)
