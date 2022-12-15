import math
from dataclasses import dataclass, astuple


@dataclass(frozen=True)
class Vector:
    x: float
    y: float

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar):
        return Vector(scalar * self.x, scalar * self.y)

    def __rmul__(self, scalar):
        return self.__mul__(scalar)

    def __iter__(self):
        return iter(astuple(self))

    def __truediv__(self, scalar):
        return Vector(self.x / scalar, self.y / scalar)

    def __floordiv__(self, scalar):
        return Vector(self.x // scalar, self.y // scalar)

    def length(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)


@dataclass(frozen=True)
class BoundingBox:
    position: Vector
    size: Vector

    def contains(self, point: Vector):
        return self.position.x <= point.x <= self.position.x + self.size.x \
               and self.position.y <= point.y <= self.position.y + self.size.y