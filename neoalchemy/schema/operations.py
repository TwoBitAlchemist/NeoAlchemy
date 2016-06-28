

class OperatorInterface(object):

    # Mathematical Operators
    def __add__(self, x):         # self + x
        return '%%s.%s + %r' % (self.key, x)

    def __radd__(self, x):        # x + self
        return self.__add__(x)

    def __sub__(self, x):         # self - x
        return '%%s.%s - %r' % (self.key, x)

    def __rsub__(self, x):        # x - self
        return '%r - %%s.%s' % (x, self.key)

    def __mul__(self, x):         # self * x
        return '%%s.%s * %r' % (self.key, x)

    def __rmul__(self, x):        # x * self
        return self.__mul__(x)

    def __div__(self, x):         # self / x
        return '%%s.%s / %r' % (self.key, x)

    def __rdiv__(self, x):        # x / self
        return '%r / %%s.%s' % (x, self.key)

    def __truediv__(self, x):     # self / x  (__future__.division)
        return self.__div__(x)

    def __rtruediv__(self, x):    # x / self  (__future__.division)
        return self.__rdiv__(x)

    def __floordiv__(self, x):    # self // x
        return self.__div__(x)

    def __rfloordiv__(self, x):   # x // self
        return self.__rdiv__(x)

    def __mod__(self, x):         # self % x
        return '%%s.%s %% %r' % (self.key, x)

    def __rmod__(self, x):        # x % self
        return '%r %% %%s.%s' % (x, self.key)

    def __pow__(self, x):         # self ** x
        return '%%s.%s ^ %r' % (self.key, x)

    def __rpow__(self, x):        # x ** self
        return '%r ^ %%s.%s' % (x, self.key)

    # Comparison Operators
    def __eq__(self, x):          # self == x
        return '%%s.%s = %r' % (self.key, x)

    def __ne__(self, x):          # self != x
        return '%%s.%s <> %r' % (self.key, x)

    def __lt__(self, x):          # self < x
        return '%%s.%s < %r' % (self.key, x)

    def __gt__(self, x):          # self > x
        return '%%s.%s > %r' % (self.key, x)

    def __le__(self, x):          # self <= x
        return '%%s.%s <= %r' % (self.key, x)

    def __ge__(self, x):          # self >= x
        return '%%s.%s >= %r' % (self.key, x)
