# -*- encoding:utf-8 -*-

import math
from typing import Union


class Vector(list):
    """Represents a mathematical vector with basic operations."""

    norm = property(lambda v: pow(sum([a * a for a in v]), 0.5), None, None)

    def __repr__(self) -> str:
        """Returns a string representation of the vector."""
        return "\n".join([f"{a: 5f}" for a in self]) 
    
    def __add__(self, v: "Vector") -> "Vector":
        """
        Performs vector addition.
        
        Args:
            v (Vector): The vector to add.
        
        Returns:
            Vector: The resulting vector after addition.
        """
        return Vector([a + b for a, b in zip(self, v)])

    def __sub__(self, v: "Vector") -> "Vector":
        """
        Performs vector subtraction.
        
        Args:
            v (Vector): The vector to subtract.
        
        Returns:
            Vector: The resulting vector after subtraction.
        """
        return Vector([a - b for a, b in zip(self, v)])

    def __neg__(self) -> "Vector":
        """
        Returns the negation of the vector.
        
        Returns:
            Vector: The negated vector.
        """
        return -1 * self

    def __truediv__(self, k: float) -> "Vector":
        """
        Divides the vector by a scalar.
        
        Args:
            k (float): The scalar to divide by.
        
        Returns:
            Vector: The resulting vector after division.
        """
        if hasattr(k, "__iter__"):
            raise ValueError(f"{k} have to be a scalar")
        else:
            return Vector([a / k for a in self])

    def __floordiv__(self, k: float) -> "Vector":
        """
        Performs floor division of the vector by a scalar.
        
        Args:
            k (float): The scalar to divide by.
        
        Returns:
            Vector: The resulting vector after floor division.
        """
        if hasattr(k, "__iter__"):
            raise ValueError(f"{k} have to be a scalar")
        else:
            return Vector([a // k for a in self])

    def __mul__(self, v: Union[float, "Vector"]) -> Union[float, "Vector"]:
        """
        Performs scalar multiplication or dot product.
        
        Args:
            v (Union[float, Vector]): The scalar or vector to multiply.
        
        Returns:
            Union[float, Vector]: The resulting vector or scalar after
                                  multiplication.
        """
        if hasattr(v, "__iter__"):
            return sum(a * b for a, b in zip(self, v))
        else:
            return Vector([a * v for a in self])
    __rmul__ = __mul__

    def __matmul__(self, v: "Vector") -> "Vector":
        """
        Computes the cross product of two vectors (2D or 3D).
        
        Args:
            v (Vector): The other vector.
        
        Returns:
            Vector: The cross product of self and v.
        """
        if len(v) > 3 or len(self) > 3:
            raise NotImplementedError("Only perform 2D or 3D operation")
        if len(v) < 3:
            v += [0.] * (3-len(v))
        if len(self) < 3:
            self += [0.] * (3-len(self))
        return Vector([
            self[1] * v[2] - self[2] * v[1],
            self[2] * v[0] - self[0] * v[2],
            self[0] * v[1] - self[1] * v[0]
        ])

    def normalize(self) -> "Vector":
        """
        Returns the normalized vector.
        
        Returns:
            Vector: The normalized vector.
        """
        return self / self.norm


class Matrix(list):
    """Represents a mathematical matrix with vector operations."""

    def __init__(self, *vectors):
        """
        Initializes a matrix from multiple vectors.
        
        Args:
            *vectors (Vector): The vectors forming the matrix.
        """
        row = max(len(vect) for vect in vectors)
        for vector in vectors:
            n = len(vector)
            if n < row:
                vector += [0.] * (row-n)
            self.append(vector)

    def __repr__(self) -> str:
        """Returns a string representation of the matrix."""
        return f"\n".join([
            " ".join([f"{a: 5f}" for a in vector])
            for vector in self.transpose()
        ])

    def __matmul__(self, elem: Union[float, Vector, "Matrix"]) -> "Matrix":
        """
        Performs matrix-vector or matrix-matrix multiplication.
        
        Args:
            elem: A vector or another matrix.
        
        Returns:
            The resulting vector or matrix.
        
        Raises:
            ValueError: If dimensions do not match.
        """
        if isinstance(elem, Vector): 
            if len(self) != len(elem):
                raise ValueError(f"Vector size should be {len(self)}")
            return Vector(
                [col * elem for col in [Vector(elem) for elem in zip(*self)]]
            )
        elif isinstance(elem, Matrix):
            if len(self) != len(elem[0]):
                raise ValueError(f"Matrix line number should be {len(self)}")
            t = [Vector(elem) for elem in zip(*self)]
            return Matrix(
                *[Vector([col1 * col2 for col1 in t]) for col2 in elem]
            ) 
        else:
            return Matrix(*[elem * vector for vector in self])

    @staticmethod
    def ned2efec(lon: float, lat: float) -> "Matrix":
        """
        Computes the transformation matrix from NED to ECEF coordinates.
        
        Args:
            lon: Longitude in degrees.
            lat: Latitude in degrees.
        
        Returns:
            A 3x3 transformation matrix.
        """
        lon = math.radians(lon); lat = math.radians(lat)
        cl = math.cos(lon); sl = math.sin(lon)
        cp = math.cos(lat); sp = math.sin(lat)
        return Matrix(
            Vector([-sp*cl, -sp*sl, cp]),
            Vector([-sl, cl, 0.]),
            Vector([-cp*cl, -cp*sl, -sp])
        )

    def transpose(self) -> "Matrix":
        """
        Computes the transpose of the matrix.

        Returns:
            Matrix: The transposed matrix.
        """
        return Matrix(*[Vector(elem) for elem in zip(*self)])


class Point(Vector):
    """Represents a point with optional uncertainty values."""

    def __init__(self, *args, **kwargs):
        """
        Initializes a point with optional dx, dy, dz attributes.

        Args:
            *args: Positional arguments for the vector components.
            **kwargs: Keyword arguments for uncertainties (dx, dy, dz).
        """
        self.dx = kwargs.pop("dx", 0.)
        self.dy = kwargs.pop("dy", 0.)
        self.dz = kwargs.pop("dz", 0.)
        Vector.__init__(self, *args, **kwargs)

    def __add__(self, v: Union["Point", Vector]) -> "Point":
        """
        Adds a vector to a point component-wise.

        Args:
            v (Vector): The vector to add.

        Returns:
            Point: The resulting point after addition.
        """
        dx = self.dx + getattr(v, "dx", self.dx) / 2.0
        dy = self.dy + getattr(v, "dy", self.dy) / 2.0
        dz = self.dz + getattr(v, "dz", self.dz) / 2.0
        return Point([a + b for a, b in zip(self, v)], dx=dx, dy=dy, dz=dz)

    def __sub__(self, v: Union["Point", Vector]) -> "Point":
        """
        Subtracts a vector from a point component-wise.

        Args:
            v (Vector): The vector to subtract.

        Returns:
            Point: The resulting point after subtraction.
        """
        dx = self.dx + getattr(v, "dx", self.dx) / 2.0
        dy = self.dy + getattr(v, "dy", self.dy) / 2.0
        dz = self.dz + getattr(v, "dz", self.dz) / 2.0
        return Point([a - b for a, b in zip(self, v)], dx=dx, dy=dy, dz=dz)

    def __repr__(self) -> str:
        """Returns a string representation of the point with uncertainties."""
        return f"{Vector.__repr__(self)}\n"\
               f"<dx={self.dx} dy={self.dy} dz={self.dz}>"


def barycentre(*points) -> Point:
    """
    Computes the weighted barycenter of given points.
    
    Args:
        *points (Union[Vector, Point]): The list of points to compute the
                                        barycenter.
    
    Returns:
        Vector: The computed barycenter.
    """
    x, y, z = [], [], []
    dx, dy, dz = [], [], []
    n = len(points)

    for point in points:
        x += [point[0]]
        dx += [getattr(point, "dx", 0.)]
        y += [point[1]]
        dy += [getattr(point, "dy", 0.)]
        z += [point[2]]
        dz += [getattr(point, "dz", 0.)]

    max_dx = (max(dx) or 1.0); min_dx = min(dx) / max_dx; 
    max_dy = (max(dy) or 1.0); min_dy = min(dy) / max_dy; 
    max_dz = (max(dz) or 1.0); min_dz = min(dz) / max_dz; 

    kx = [(min_dx + 1.0 - k / max_dx) for k in dx]
    ky = [(min_dy + 1.0 - k / max_dy) for k in dy]
    kz = [(min_dz + 1.0 - k / max_dz) for k in dz]

    return Point([
            sum(a * k for a, k in zip(x, kx)) / sum(kx),
            sum(a * k for a, k in zip(y, ky)) / sum(ky),
            sum(a * k for a, k in zip(z, kz)) / sum(kz)
        ], dx=sum(dx)/n, dy=sum(dy)/n, dz=sum(dz)/n
    )


def triangulate(
    A: Union[Point, Vector], u: Vector, B: Union[Point, Vector], v: Vector
) -> Point:
    """
    Computes the intersection point of two lines given by points A, B and
    vectors u, v.
        
    Args:
        A (Union[Point, Vector]): A point on the first line.
        u (Vector): Direction vector of the first line.
        B (Union[Point, Vector]): A point on the second line.
        v (Vector): Direction vector of the second line.
    
    Returns:
        Vector: The computed intersection point.
    """
    u = u.normalize()
    v = v.normalize()

    C = A - B
    Cu = C * u
    Cv = C * v
    alpha = u * v
    alpha2 = alpha * alpha

    if alpha2 == 1.0:
        raise ValueError("No convergence possible")

    return Point(
        barycentre(
            (A + (alpha*Cv - Cu) / (1 - alpha2) * u),
            (B + (Cv - alpha*Cu) / (1 - alpha2) * v)
        ),
        dx = (getattr(A, "dx", 0.) + getattr(B, "dx", 0.)) / 2,
        dy = (getattr(A, "dy", 0.) + getattr(B, "dy", 0.)) / 2,
        dz = (getattr(A, "dz", 0.) + getattr(B, "dz", 0.)) / 2
    )


def localize(*items):
    points = []
    for i in range(0, len(items)-1, 1):
        for j in range(i+1, len(items), 1):
            points.append(triangulate(*items[i], *items[j]))
    return barycentre(*points)


if __name__ == "__main__":
    m = Matrix.ned2efec(5.0, 45.0)
    A = Point([0, 0, 0], dx=1, dy=1, dz=5)
    B = Point([10, 0, 10], dx=1, dy=2, dz=10)
    C = Point([10, 0, 0], dx=1, dy=2, dz=10)
    u = Vector([-0.02, 10., 0])
    v = Vector([-0.02, 10., 0])
    w = Vector([-0.02, 10., 0])

    print(m[0] @ m[1], "\n\n", m[2], sep="")
    print("\n", m @ m.transpose(), sep="")
    print("\n", localize((A, u), (C, w), ), sep="")
