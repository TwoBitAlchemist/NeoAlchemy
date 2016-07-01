

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
                 node_key=None, property_name=None, reverse=False):
        self.operator = operator
        self.value = value
        self.node_key = node_key
        self.property_name = property_name
        self.reverse = reverse
        self.param_id = None

    @property
    def param_key(self):
        if self.node_key:
            return '%s_%s' % (self.property_name, self.node_key)
        return self.property_name

    def __eq__(self, x):
        return CypherExpressionList([self, self.__class__('=', x)])

    def __and__(self, x):
        return CypherExpressionList([self, 'AND', x])

    def __or__(self, x):
        return CypherExpressionList([self, 'OR', x])

    def __str__(self):
        key = '.'.join(key for key in (self.node_key, self.property_name) if key)
        expr = [key, self.operator, '{%s}' % self.param_key]
        return ' '.join(expr if not self.reverse else reversed(expr))


class OperatorInterface(object):
    # Mathematical Operators
    def __add__(self, x):         # self + x
        return CypherExpression('+', x)

    def __radd__(self, x):        # x + self
        return self.__add__(x)

    def __sub__(self, x):         # self - x
        return CypherExpression('-', x)

    def __rsub__(self, x):        # x - self
        return CypherExpression('-', x)

    def __mul__(self, x):         # self * x
        return CypherExpression('*', x)

    def __rmul__(self, x):        # x * self
        return self.__mul__(x)

    def __div__(self, x):         # self / x
        return CypherExpression('/', x)

    def __rdiv__(self, x):        # x / self
        return CypherExpression('/', x, reverse=True)

    def __truediv__(self, x):     # self / x  (__future__.division)
        return self.__div__(x)

    def __rtruediv__(self, x):    # x / self  (__future__.division)
        return self.__rdiv__(x)

    def __floordiv__(self, x):    # self // x
        return self.__div__(x)

    def __rfloordiv__(self, x):   # x // self
        return self.__rdiv__(x)

    def __mod__(self, x):         # self % x
        return CypherExpression('%', x)

    def __rmod__(self, x):        # x % self
        return CypherExpression('%', x, reverse=True)

    def __pow__(self, x):         # self ** x
        return CypherExpression('^', x)

    def __rpow__(self, x):        # x ** self
        return CypherExpression('^', x, reverse=True)

    # Comparison Operators
    def __eq__(self, x):          # self == x
        return CypherExpression('=', x, property_name=self.name)

    def __ne__(self, x):          # self != x
        return CypherExpression('<>', x, property_name=self.name)

    def __lt__(self, x):          # self < x
        return CypherExpression('<', x, property_name=self.name)

    def __gt__(self, x):          # self > x
        return CypherExpression('>', x, property_name=self.name)

    def __le__(self, x):          # self <= x
        return CypherExpression('<=', x, property_name=self.name)

    def __ge__(self, x):          # self >= x
        return CypherExpression('>=', x, property_name=self.name)