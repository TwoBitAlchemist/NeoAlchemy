

class OperatorInterface(object):

    # Mathematical Operators
    def __add__(self, x):
        pass    # self + x

    def __radd__(self, x):
        pass    # x + self

    def __sub__(self, x):
        pass    # self - x

    def __rsub__(self, x):
        pass    # x - self

    def __mul__(self, x):
        pass    # self * x

    def __rmul__(self, x):
        pass    # x * self

    def __div__(self, x):
        pass    # self / x

    def __rdiv__(self, x):
        pass    # x / self

    def __truediv__(self, x):
        pass    # self / x  __future__.division

    def __rtruediv__(self, x):
        pass    # x / self  __future__.division

    def __floordiv__(self, x):
        pass    # self // x

    def __rfloordiv__(self, x):
        pass    # x // self

    def __mod__(self, x):
        pass    # self % x

    def __rmod__(self, x):
        pass    # x % self

    def __pow__(self, x):
        pass    # self ** x

    def __rpow__(self, x):
        pass    # x ** self

    # Comparison Operators
    def __eq__(self, x):
        pass    # self == x

    def __ne__(self, x):
        pass    # self != x

    def __lt__(self, x):
        pass    # self < x

    def __gt__(self, x):
        pass    # self > x

    def __lte__(self, x):
        pass    # self <= x

    def __gte__(self, x):
        pass    # self >= x

    # Logical Operators
    def __and__(self, x):
        pass    # self & x

    def __rand__(self, x):
        pass    # x & self

    def __or__(self, x):
        pass    # self | x

    def __ror__(self, x):
        pass    # x | self

    def __xor__(self, x):
        pass    # self ^ x

    def __rxor__(self, x):
        pass    # x ^ self
