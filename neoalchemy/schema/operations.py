

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
    def __init__(self, operator, value, property_,
                 node_key=None, reverse=False):
        self.operator = operator
        self.node_key = node_key
        self.property_ = property_
        self.value = self.property_.type(value)
        self.reverse = reverse

    def __eq__(self, x):
        other = self.__class__('=', x, self.property_, node_key='')
        return CypherExpressionList([self, other])

    def __and__(self, x):
        return CypherExpressionList([self, 'AND', x])

    def __or__(self, x):
        return CypherExpressionList([self, 'OR', x])

    def __str__(self):
        if self.node_key:
            expr = ['%s.%s' % (self.node_key, self.property_.name)]
        else:
            expr = []
        expr += [self.operator, '{%s}' % self.param_key]
        return ' '.join(expr if not self.reverse else reversed(expr))


class LogicalCypherExpression(CypherExpression):
    @property
    def param_key(self):
        if self.node_key:
            return '%s_%s' % (self.property_.name, self.node_key)


class ArithmeticCypherExpression(CypherExpression):
    def __init__(self, *args, **kw):
        self.param_key = None
        super(ArithmeticCypherExpression, self).__init__(*args, **kw)


class OperatorInterface(object):
    # Mathematical Operators
    def __add__(self, x):         # self + x
        return ArithmeticCypherExpression('+', x, self)

    def __radd__(self, x):        # x + self
        return self.__add__(x)

    def __sub__(self, x):         # self - x
        return ArithmeticCypherExpression('-', x, self)

    def __rsub__(self, x):        # x - self
        return ArithmeticCypherExpression('-', x, self, reverse=True)

    def __mul__(self, x):         # self * x
        return ArithmeticCypherExpression('*', x, self)

    def __rmul__(self, x):        # x * self
        return self.__mul__(x)

    def __div__(self, x):         # self / x
        return ArithmeticCypherExpression('/', x, self)

    def __rdiv__(self, x):        # x / self
        return ArithmeticCypherExpression('/', x, self, reverse=True)

    def __truediv__(self, x):     # self / x  (__future__.division)
        return self.__div__(x)

    def __rtruediv__(self, x):    # x / self  (__future__.division)
        return self.__rdiv__(x)

    def __floordiv__(self, x):    # self // x
        return self.__div__(x)

    def __rfloordiv__(self, x):   # x // self
        return self.__rdiv__(x)

    def __mod__(self, x):         # self % x
        return ArithmeticCypherExpression('%', x, self)

    def __rmod__(self, x):        # x % self
        return ArithmeticCypherExpression('%', x, self, reverse=True)

    def __pow__(self, x):         # self ** x
        return ArithmeticCypherExpression('^', x, self)

    def __rpow__(self, x):        # x ** self
        return ArithmeticCypherExpression('^', x, self, reverse=True)

    # Comparison Operators
    def __eq__(self, x):          # self == x
        return LogicalCypherExpression('=', x, self)

    def __ne__(self, x):          # self != x
        return LogicalCypherExpression('<>', x, self)

    def __lt__(self, x):          # self < x
        return LogicalCypherExpression('<', x, self)

    def __gt__(self, x):          # self > x
        return LogicalCypherExpression('>', x, self)

    def __le__(self, x):          # self <= x
        return LogicalCypherExpression('<=', x, self)

    def __ge__(self, x):          # self >= x
        return LogicalCypherExpression('>=', x, self)
