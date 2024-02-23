# -*- encoding:utf-8 -*-

import ctypes


class Unit(ctypes.Structure):
    """
    Represents a `Unit` structure in C code.

    Attributes:
        ratio (float): The ratio value of the unit.
    """

    _fields_ = [("ratio", ctypes.c_double)]


class Prime(ctypes.Structure):
    """
    Represents a `Prime` structure in C code.

    Attributes:
        longitude (float): The longitude value of the prime meridian.
    """

    _fields_ = [("longitude", ctypes.c_double)]


class Ellipsoid(ctypes.Structure):
    """
    Represents an `Ellipsoid` structure in C code.

    Attributes:
        a (float): The semi-major axis of the ellipsoid.
        b (float): The semi-minor axis of the ellipsoid.
        e (float): The eccentricity of the ellipsoid.
        f (float): The flattening of the ellipsoid.
    """

    _fields_ = [
        ("a", ctypes.c_double),
        ("b", ctypes.c_double),
        ("e", ctypes.c_double),
        ("f", ctypes.c_double)
    ]


class Datum(ctypes.Structure):
    """
    Represents a `Datum` structure in C code.

    Attributes:
        ellipsoid (Ellipsoid): The ellipsoid associated with the datum.
        prime (Prime): The prime meridian associated with the datum.
        ds (float): The scale difference parameter.
        dx (float): The X translation parameter.
        dy (float): The Y translation parameter.
        dz (float): The Z translation parameter.
        rx (float): The X rotation parameter.
        ry (float): The Y rotation parameter.
        rz (float): The Z rotation parameter.
    """

    _fields_ = [
        ("ellipsoid", Ellipsoid),
        ("prime", Prime),
        ("ds", ctypes.c_double),
        ("dx", ctypes.c_double),
        ("dy", ctypes.c_double),
        ("dz", ctypes.c_double),
        ("rx", ctypes.c_double),
        ("ry", ctypes.c_double),
        ("rz", ctypes.c_double)
    ]


class Crs(ctypes.Structure):
    """
    Represents a `Crs` structure in C code.

    Attributes:
        datum (Datum): The datum associated with the coordinate reference
            system.
        lambda0 (float): The lambda0 parameter.
        phi0 (float): The phi0 parameter.
        phi1 (float): The phi1 parameter.
        phi2 (float): The phi2 parameter.
        k0 (float): The k0 parameter.
        x0 (float): The x0 parameter.
        y0 (float): The y0 parameter.
        azimut (float): The azimuth parameter.
    """

    _fields_ = [
        ("datum", Datum),
        ("lambda0", ctypes.c_double),
        ("phi0", ctypes.c_double),
        ("phi1", ctypes.c_double),
        ("phi2", ctypes.c_double),
        ("k0", ctypes.c_double),
        ("x0", ctypes.c_double),
        ("y0", ctypes.c_double),
        ("azimut", ctypes.c_double)
    ]
