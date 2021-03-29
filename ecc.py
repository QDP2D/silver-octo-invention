primeOfFiniteField = 2**256 - 2**32 - 977
A = 0
B = 7
# x-coordinate of generator point
GX = 0x79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798
# y-coordinate of generator point
GY = 0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8
# "order of" the generator point
N = 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141


class Signature:
    def __init__(self, r, s):
        self.r = r
        self.s = s

    def __repr__(self):
        return 'Signature({:x}, {:x})'.format(self.r, self.s)


class FieldElement:
    def __init__(self, num, prime):
        if num >= prime or num < 0:
            error = 'Num {} not in field range 0 to {}'.format(num, prime - 1)
            raise ValueError(error)
        self.num = num
        self.prime = prime

    def __repr__(self):
        return 'FieldElement_{} ({})'.format(self.num, self.prime - 1)

    def __eq__(self, other):
        if other is None:
            return False
        return self.num == other.num and self.prime == other.prime

    def __ne__(self, other):
        if other is None:
            return True
        return self.num != other.num or self.prime != self.prime != other.prime

    def __add__(self, other):
        if self.prime != other.prime:
            raise TypeError('Cannot add two numbers in different fields')
        num = (self.num + other.num) % self.prime
        return self.__class__(num, self.prime)

    def __sub__(self, other):
        if self.prime != other.prime:
            raise TypeError('Cannot subtract two numbers in different fields')
        num = (self.num - other.num) % self.prime
        return self.__class__(num, self.prime)

    def __mul__(self, other):
        if self.prime != other.prime:
            raise TypeError('Cannot multiply two numbers in different fields')
        num = (self.num * other.num) % self.prime
        return self.__class__(num, self.prime)

    def __pow__(self, exponent):
        num = pow(self.num, exponent, self.prime)
        return self.__class__(num, self.prime)

    def __truediv__(self, other):
        if self.prime != other.prime:
            raise TypeError('Cannot divide two numbers in different Fields')
        num = (self.num * pow(other.num, self.prime - 2,
                              self.prime)) % self.prime
        return self.__class__(num, self.prime)


class Point:
    def __init__(self, x, y, a, b):
        self.a = a
        self.b = b
        self.x = x
        self.y = y
        # Do not check if point at infinity
        if self.x is None and self.y is None:
            return
        if self.y**2 != self.x**3 + a * x + b:
            raise ValueError('({}, {}) is not on the curve'.format(x, y))

    def __repr__(self):
        if self.x is None:
            return 'Point(infinity)'
        else:
            return 'Point({},{})_{}_{}'.format(self.x, self.y, self.a, self.b)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y \
            and self.a == other.a and self.b == other.b

    def __ne__(self, other):
        return self.x != other.x or self.y != other.y \
            or self.a != other.a or self.y != other.y

    def __add__(self, other):
        if self.a != other.a or self.b != other.b:
            raise TypeError(
                'Points {}, {} are not on the same curve'.format(self, other))
        # Self is the point at infinity
        if self.x is None:
            return other
        # Other is the point at infinity
        if other.x is None:
            return self
        # Points are opposite each other over the x-axis (additive inverses)
        if self.x == other.x and self.y != other.y:
            return self.__class__(None, None, self.a, self.b)
        # Points have different x values
        if self.x != other.x:
            slope = (other.y - self.y) / (other.x - self.x)
            x3 = slope**2 - self.x - other.x
            y3 = slope * (self.x - x3) - self.y
            return self.__class__(x3, y3, self.a, self.b)
        # Points are the same and y coordinate is 0
        if self == other and self.y == 0:
            return self.__class__(None, None, self.a, self.b)
        # Points are the same
        if self == other:
            slopeOfTangent = (3 * self.x**2 + self.a)/(2*self.y)
            x3 = slopeOfTangent**2 - 2 * self.x
            y3 = slopeOfTangent * (self.x - x3) - self.y
            return self.__class__(x3, y3, self.a, self.b)

    def __rmul__(self, coef):
        coefCopy = coef
        curr = self
        result = self.__class__(None, None, self.a, self.b)
        while coefCopy:
            if coefCopy & 1:
                result += curr
            curr += curr
            coefCopy >>= 1
        return result


class S256Field(FieldElement):
    def __init__(self, num, prime=None):
        super().__init__(num=num, prime=primeOfFiniteField)

    def __repr__(self):
        return '{:x}'.format(self.num).zfill(64)


class S256Point(Point):
    def __init__(self, x, y, a=None, b=None):
        a, b = S256Field(A), S256Field(B)
        if type(x) == int:
            super().__init__(x=S256Field(x), y=S256Field(y), a=a, b=b)
        else:  # handle case if initializing with point at infinity
            super().__init__(x=x, y=y, a=a, b=b)

    def __rmul__(self, coef):
        coefModN = coef % N
        return super().__rmul__(coefModN)


# generator point
G = S256Point(GX, GY)
