# -*- encoding:utf-8 -*-

import os
import sys
import math
import ctypes

from epsg import dataset
from epsg.geodesy import Geodesic, _dms

_TORAD = math.pi/180.0
_TODEG = 180.0/math.pi


# find data file
def _get_file(name: str) -> str:
    """
    Find data file according to package installation path.
    """
    for path in __path__:
        filename = os.path.join(path, name)
        if os.path.exists(filename):
            return filename
    raise IOError("%s data file not found" % name)


class Geocentric(ctypes.Structure):
    """
    `ctypes` structure for geocentric coordinates. This reference is generaly
    used as a transition for geodesic conversion.

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

    def __repr__(self):
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

    def __repr__(self):
        return f"<X={self.x:.3f} Y={self.y:.3f} alt={self.altitude:.3f}>"


class Vincenty_dist(ctypes.Structure):
    """
    Great circle distance computation result using Vincenty formulae.
    `Vincenty_dist` structures are returned by `Gryd.Ellipsoid.distance`
    function.

    Attributes:
        distance (float): great circle distance in meters
        initial_bearing (float): initial bearing in degrees
        final_bearing (float): final bearing in degrees
    """
    _fields_ = [
        ("distance", ctypes.c_double),
        ("initial_bearing", ctypes.c_double),
        ("final_bearing", ctypes.c_double)
    ]

    def __repr__(self):
        return "<Dist %.3fkm initial bearing=%.1f° final bearing=%.1f°>" % (
            self.distance/1000,
            math.degrees(self.initial_bearing),
            math.degrees(self.final_bearing)
        )


class Vincenty_dest(ctypes.Structure):
    """
    Great circle destination computation result using Vincenty formulae.
    `Vincenty_dist` structures are returned by `Gryd.Ellipsoid.destination`
    function.

    Attributes:
        longitude (float): destination longitude in degrees
        latitude (float): destination latitude in degrees
        destination_bearing (float): destination bearing in degrees
    """
    _fields_ = [
        ("longitude", ctypes.c_double),
        ("latitude", ctypes.c_double),
        ("destination_bearing", ctypes.c_double)
    ]

    def __repr__(self):
        return "<Dest lon=%s lat=%s end bearing=%.1f°>" % (
            _dms(math.degrees(self.longitude)),
            _dms(math.degrees(self.latitude)),
            math.degrees(self.destination_bearing)
        )


class ProjectedCoordRefSystem(dataset.EpsgElement):
    _fields_ = [
        ("datum", dataset.GeodeticCoordRefSystem),
        ("lambda0", ctypes.c_double),
        ("phi0", ctypes.c_double),
        ("phi1", ctypes.c_double),
        ("phi2", ctypes.c_double),
        ("k0", ctypes.c_double),
        ("x0", ctypes.c_double),
        ("y0", ctypes.c_double),
        ("azimut", ctypes.c_double)
    ]

    def __call__(self, element):
        ratio = self.unit.ratio
        if isinstance(element, Geodesic):
            lla = Geodesic(
                (element.longitude + self.datum.prime.longitude) * _TODEG,
                element.latitude * _TODEG, element.altitude
            )
            xya = self.forward(lla)
            xya.x /= ratio
            xya.y /= ratio
            return xya
        else:
            xya = Geographic(
                element.x * ratio, element.y * ratio, element.altitude
            )
            lla = self.inverse(xya)
            lla.longitude -= self.datum.prime.longitude
            return lla

    def forward(self, lla: Geodesic) -> Geographic:
        return self._proj_forward(self, lla)

    def inverse(self, xya: Geographic) -> Geodesic:
        return self._proj_inverse(self, xya)

    def __init__(self, *a, **kw):
        dataset.EpsgElement.__init__(self, *a, **kw)
        self.conversion = dataset.Conversion(self.Projection["Code"])
        self.projection = dataset.CoordOperationMethod(
            self.conversion.Method["Code"]
        )
        self.datum = dataset.GeodeticCoordRefSystem(
            self.BaseCoordRefSystem["Code"]
        )
        self.unit = dataset.Unit(
            dataset.CoordSystem(self.CoordSys["Code"]).Axis[0]["Unit"]["Code"]
        )

        self.parameters = []
        for param in self.conversion.ParameterValues:
            code = param["ParameterCode"]
            if code in dataset.PROJ_PARAMETER_CODES:
                attr = dataset.PROJ_PARAMETER_CODES[code]
                setattr(
                    self, attr, param["ParameterValue"] *
                    (1.0 if attr in "x0y0k0" else _TORAD)
                )
                self.parameters.append(dataset.CoordOperationParameter(code))

        name = dataset.PROJ_METHOD_CODES.get(self.projection.id, False)
        if name:
            self._proj_forward = getattr(proj, f"{name}_forward")
            self._proj_forward.restype = Geographic
            self._proj_forward.argtypes = [
                ctypes.POINTER(ProjectedCoordRefSystem),
                ctypes.POINTER(Geodesic)
            ]
            self._proj_inverse = getattr(proj, f"{name}_inverse")
            self._proj_inverse.restype = Geodesic
            self._proj_inverse.argtypes = [
                ctypes.POINTER(ProjectedCoordRefSystem),
                ctypes.POINTER(Geographic)
            ]


#######################
# loading C libraries #
#######################
# defining library name
__dll_ext__ = "dll" if sys.platform.startswith("win") else "so"
geoid = ctypes.CDLL(_get_file("geoid.%s" % __dll_ext__))
proj = ctypes.CDLL(_get_file("proj.%s" % __dll_ext__))

geoid.geocentric.argtypes = \
    [ctypes.POINTER(dataset.Ellipsoid), ctypes.POINTER(Geodesic)]
geoid.geocentric.restype = Geocentric

geoid.geodesic.argtypes = \
    [ctypes.POINTER(dataset.Ellipsoid), ctypes.POINTER(Geocentric)]
geoid.geodesic.restype = Geodesic

geoid.distance.argtypes = [
    ctypes.POINTER(dataset.Ellipsoid),
    ctypes.POINTER(Geodesic),
    ctypes.POINTER(Geodesic)
]
geoid.distance.restype = Vincenty_dist

geoid.destination.argtypes = [
    ctypes.POINTER(dataset.Ellipsoid),
    ctypes.POINTER(Geodesic),
    ctypes.POINTER(Vincenty_dist)
]
geoid.destination.restype = Vincenty_dest

# geoid.xyz_dat2dat.argtypes = [
#     ctypes.POINTER(dataset.GeodeticCoordRefSystem),
#     ctypes.POINTER(dataset.GeodeticCoordRefSystem),
#     ctypes.POINTER(Geocentric)
# ]
# geoid.xyz_dat2dat.restype = Geocentric

geoid.lla_dat2dat.argtypes = [
    ctypes.POINTER(dataset.GeodeticCoordRefSystem),
    ctypes.POINTER(dataset.GeodeticCoordRefSystem),
    ctypes.POINTER(Geodesic)
]
geoid.lla_dat2dat.restype = Geodesic
