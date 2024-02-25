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
        lambda0 (float): The longitude of the point from which the values of
            both the geographical coordinates on the ellipsoid and the grid
            coordinates on the projection are deemed to increment or decrement
            for computational purposes. Alternatively it may be considered as
            the longitude of the point which in the absence of application of
            false coordinates has grid coordinates of (0,0). Sometimes known
            as "central meridian" (CM).
        phi0 (float): The latitude of the point from which the values of both
            the geographical coordinates on the ellipsoid and the grid
            coordinates on the projection are deemed to increment or decrement
            for computational purposes. Alternatively it may be considered as
            the latitude of the point which in the absence of application of
            false coordinates has grid coordinates of (0,0).
        phi1 (float): for a conic projection with two standard parallels, this
            is the latitude of one of the parallels of intersection of the cone
            with the ellipsoid. It is normally but not necessarily that nearest
            to the pole. Scale is true along this parallel.
        phi2 (float): for a conic projection with two standard parallels, this
            is the latitude of one of the parallels at which the cone
            intersects with the ellipsoid. It is normally but not necessarily
            that nearest to the equator. Scale is true along this parallel.
        k0 (float): the factor by which the map grid is reduced or enlarged
            during the projection process, defined by its value at the natural
            origin.
        x0 (float): since the natural origin may be at or near the centre of
            the projection and under normal coordinate circumstances would thus
            give rise to negative coordinates over parts of the mapped area,
            this origin is usually given false coordinates which are large
            enough to avoid this inconvenience. The False Easting, FE, is the
            value assigned to the abscissa (east or west) axis of the
            projection grid at the natural origin.
        y0 (float): since the natural origin may be at or near the centre of
            the projection and under normal coordinate circumstances would thus
            give rise to negative coordinates over parts of the mapped area,
            this origin is usually given false coordinates which are large
            enough to avoid this inconvenience. The False Northing, FN, is the
            value assigned to the ordinate (north or south) axis of the
            projection grid at the natural origin.
        azimut (float): the azimuthal direction (north zero, east of north
            being positive) of the great circle which is the centre line of an
            oblique projection. The azimuth is given at the projection centre.
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
