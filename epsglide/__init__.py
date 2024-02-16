# -*- encoding:utf-8 -*-

import os
import sys
import math
import ctypes
import typing

from epsglide import dataset
from epsglide.geodesy import Geodesic, _dms

_TORAD = math.pi/180.0
_TODEG = 180.0/math.pi


# find data file
def _get_file(name: str) -> str:
    """
    Find data file in epsg package pathes.
    """
    for path in __path__:
        filename = os.path.join(path, name)
        if os.path.exists(filename):
            return filename
    raise IOError("%s data file not found" % name)


class Geocentric(ctypes.Structure):
    """
    `ctypes` structure for geocentric coordinates. This reference is generaly
    used as a transition for datum transformation. Coordinates are expressed in
    metres.

    Attributes:
        x (float): X-axis value
        y (float): Y-axis value
        z (float): Z-axis value

    ```python
    >>> Gryd.Geocentric(4457584, 429216, 4526544)
    <X=4457584.000 Y=429216.000 Z=4526544.000>
    >>> Gryd.Geocentric(x=4457584, y=429216, z=4526544)
    <X=4457584.000 Y=429216.000 Z=4526544.000>
    ```
    """
    _fields_ = [
        ("x", ctypes.c_double),
        ("y", ctypes.c_double),
        ("z", ctypes.c_double)
    ]

    def __repr__(self) -> str:
        return f"<X={self.x:.3f} Y={self.y:.3f} Z={self.z:.3f}>"


class Geographic(ctypes.Structure):
    """
    `ctypes` structure for geographic coordinates ie 2D coordinates on
    flattened earth with elevation as third dimension.

    Attributes:
        x (float): X-projection-axis value
        y (float): Y-projection-axis value
        altitude (float): elevation in meters

    ```python
    >>> Gryd.Geographic(5721186, 2948518, 105)
    <X=5721186.000 Y=2948518.000 alt=105.000>
    >>> Gryd.Geographic(x=5721186, y=2948518, altitude=105)
    <X=5721186.000 Y=2948518.000 alt=105.000>
    ```
    """
    _fields_ = [
        ("x", ctypes.c_double),
        ("y", ctypes.c_double),
        ("altitude", ctypes.c_double)
    ]

    def __repr__(self) -> str:
        if hasattr(self, "_unit"):
            prefix = f"{self._unit.Name}:{self._unit.ratio:.3f}"
        else:
            prefix = "metre:1.000"
        return \
            f"<{prefix}[X={self.x:.3f} Y={self.y:.3f}]"\
            f" alt={self.altitude:.3f}>"


class Vincenty_dist(ctypes.Structure):
    """
    Great circle distance computation result using Vincenty formulae.

    Attributes:
        distance (float): great circle distance in meters
        initial_bearing (float): initial bearing in radians
        final_bearing (float): final bearing in radians
    """
    _fields_ = [
        ("distance", ctypes.c_double),
        ("initial_bearing", ctypes.c_double),
        ("final_bearing", ctypes.c_double)
    ]

    def __repr__(self) -> str:
        return \
            f"<{self.distance/1000:.3f}km "\
            f"initial bearing={math.degrees(self.initial_bearing):.1f}° "\
            f"final bearing{math.degrees(self.final_bearing):.1f}°>"


class Vincenty_dest(ctypes.Structure):
    """
    Great circle destination computation result using Vincenty formulae.

    Attributes:
        longitude (float): destination longitude in radians
        latitude (float): destination latitude in radians
        destination_bearing (float): destination bearing in radians
    """
    _fields_ = [
        ("longitude", ctypes.c_double),
        ("latitude", ctypes.c_double),
        ("destination_bearing", ctypes.c_double)
    ]

    def __repr__(self) -> str:
        return \
            f"<lon={_dms(math.degrees(self.longitude))} "\
            f"lat={_dms(math.degrees(self.latitude))} "\
            f"end bearing={math.degrees(self.destination_bearing):.1f}°>"


class ProjectedCoordRefSystem(dataset.EpsgElement):
    """
    """

    def populate(self):
        self.Datum = dataset.GeodeticCoordRefSystem(
            self.BaseCoordRefSystem["Code"]
        )
        self._struct_ = dataset.src.Crs()
        self._struct_.datum = self.Datum._struct_

        self.Conversion = dataset.Conversion(self.Projection["Code"])
        self.CoordOperationMethod = dataset.CoordOperationMethod(
            self.Conversion.Method["Code"]
        )

        coordsys = dataset.CoordSystem(self.CoordSys["Code"])
        self.x_unit = dataset.Unit(coordsys.Axis[0]["Unit"]["Code"])
        self.y_unit = dataset.Unit(coordsys.Axis[1]["Unit"]["Code"])
        self.CoordSystem = coordsys

        self.parameters = []
        for param in self.Conversion.ParameterValues:
            code = param["ParameterCode"]
            if code in dataset.PROJ_PARAMETER_CODES:
                attr = dataset.PROJ_PARAMETER_CODES[code]
                setattr(
                    self._struct_, attr, param["ParameterValue"] *
                    (1.0 if attr in "x0y0k0" else _TORAD)
                )
                self.parameters.append(dataset.CoordOperationParameter(code))

        name = dataset.PROJ_METHOD_CODES.get(
            self.CoordOperationMethod.id, False
        )
        if name:
            self._proj_forward = getattr(proj, f"{name}_forward")
            self._proj_forward.restype = Geographic
            self._proj_forward.argtypes = [
                ctypes.POINTER(dataset.src.Crs),
                ctypes.POINTER(Geodesic)
            ]
            self._proj_inverse = getattr(proj, f"{name}_inverse")
            self._proj_inverse.restype = Geodesic
            self._proj_inverse.argtypes = [
                ctypes.POINTER(dataset.src.Crs),
                ctypes.POINTER(Geographic)
            ]

    def __call__(self, element: typing.Union[Geodesic, Geographic]) \
            -> typing.Union[Geodesic, Geographic]:
        """
        """

        if isinstance(element, Geodesic):
            longitude = element.longitude + self._struct_.datum.prime.longitude
            lla = Geodesic(
                longitude * _TODEG, element.latitude * _TODEG, element.altitude
            )
            xya = self.forward(lla)
            xya.x /= self.x_unit.ratio
            xya.y /= self.y_unit.ratio
            setattr(xya, "_unit", self.x_unit)
            return xya
        else:
            xya = Geographic(
                element.x * self.x_unit.ratio, element.y * self.y_unit.ratio,
                element.altitude
            )
            lla = self.inverse(xya)
            lla.longitude -= self._struct_.datum.prime.longitude
            return lla

    def forward(self, lla: Geodesic) -> Geographic:
        return self._proj_forward(self._struct_, lla)

    def inverse(self, xya: Geographic) -> Geodesic:
        return self._proj_inverse(self._struct_, xya)


#######################
# loading C libraries #
#######################
# defining library name
__dll_ext__ = "dll" if sys.platform.startswith("win") else "so"
geoid = ctypes.CDLL(_get_file("geoid.%s" % __dll_ext__))
proj = ctypes.CDLL(_get_file("proj.%s" % __dll_ext__))

geoid.geocentric.argtypes = \
    [ctypes.POINTER(dataset.src.Ellipsoid), ctypes.POINTER(Geodesic)]
geoid.geocentric.restype = Geocentric

geoid.geodesic.argtypes = \
    [ctypes.POINTER(dataset.src.Ellipsoid), ctypes.POINTER(Geocentric)]
geoid.geodesic.restype = Geodesic

geoid.distance.argtypes = [
    ctypes.POINTER(dataset.src.Ellipsoid),
    ctypes.POINTER(Geodesic),
    ctypes.POINTER(Geodesic)
]
geoid.distance.restype = Vincenty_dist

geoid.destination.argtypes = [
    ctypes.POINTER(dataset.src.Ellipsoid),
    ctypes.POINTER(Geodesic),
    ctypes.POINTER(Vincenty_dist)
]
geoid.destination.restype = Vincenty_dest

geoid.lla_dat2dat.argtypes = [
    ctypes.POINTER(dataset.src.Crs),
    ctypes.POINTER(dataset.src.Crs),
    ctypes.POINTER(Geodesic)
]
geoid.lla_dat2dat.restype = Geodesic


dataset.Ellipsoid.distance = lambda obj, start, stop: \
    geoid.distance(obj._struct_, start, stop)


dataset.Ellipsoid.destination = lambda obj, start, dist: \
    geoid.destination(obj._struct_, start, dist)
