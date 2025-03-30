# -*- encoding:utf-8 -*-

"""
This package aims to perform simple requests to [`EPSG GeoRepository API`](htt\
ps://apps.epsg.org/api/swagger/ui/index) and provides associated geodesic
computation and map projection.
"""

import os
import sys
import math
import ctypes
import typing

from epsglide import dataset, geodesy

_TORAD = math.pi/180.0
_TODEG = 180.0/math.pi

try:
    WGS84 = dataset.GeodeticCoordRefSystem(4326)
except Exception:
    WGS84 = None


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


class Geodetic(geodesy.Geodetic):
    __doc__ = geodesy.Geodetic.__doc__

    def xyz(self, ellps: dataset.Ellipsoid):
        return geoid.geocentric(ellps._struct_, self)


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
    >>> epsglide.Geocentric(4457584, 429216, 4526544)
    <X=4457584.000 Y=429216.000 Z=4526544.000>
    >>> epsglide.Geocentric(x=4457584, y=429216, z=4526544)
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
    
    def lla(self, ellps: dataset.Ellipsoid):
        return geoid.geodetic(ellps._struct_, self)


class Geographic(ctypes.Structure):
    """
    `ctypes` structure for geographic coordinates ie 2D coordinates on
    flattened earth with elevation as third dimension.

    Attributes:
        x (float): X-projection-axis value
        y (float): Y-projection-axis value
        altitude (float): elevation in meters

    ```python
    >>> epsglide.Geographic(5721186, 2948518, 105)
    <X=5721186.000 Y=2948518.000 alt=105.000>
    >>> epsglide.Geographic(x=5721186, y=2948518, altitude=105)
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
            f"<{prefix}[X={self.x:.3f} Y={self.y:.3f}]" \
            f" alt={self.altitude:.3f}>"


class Vincenty_dist(ctypes.Structure):
    r"""
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
            f"<{self.distance/1000:.3f}km " \
            f"initial bearing={math.degrees(self.initial_bearing):.1f}° " \
            f"final bearing={math.degrees(self.final_bearing):.1f}°>"


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
            f"<lon={geodesy._dms(math.degrees(self.longitude))} " \
            f"lat={geodesy._dms(math.degrees(self.latitude))} " \
            f"end bearing={math.degrees(self.destination_bearing):.1f}°>"


def distance(
    obj: dataset.Ellipsoid, start: Geodetic, stop: Geodetic
) -> Vincenty_dist:
    """
    Calculate the distance between two points on the ellipsoid surface.

    Args:
        obj (dataset.Ellipsoid): The ellipsoid object representing the shape of
            the Earth.
        start (Geodetic): The starting point.
        stop (Geodetic): The destination point.

    Returns:
        Vincenty_dist: The distance between the two points.
    """
    return geoid.distance(obj._struct_, start, stop)


def destination(
    obj: dataset.Ellipsoid, start: Geodetic, dist: Vincenty_dist
) -> Vincenty_dest:
    """
    Calculate the destination point given start point, initial bearing, and
    distance.

    Args:
        obj (dataset.Ellipsoid): The ellipsoid object representing the shape of
            the Earth.
        start (Geodetic): The starting point.
        dist (Vincenty_dist): The distance to travel.

    Returns:
        Vincenty_dest: The destination point.
    """
    return geoid.destination(obj._struct_, start, dist)


def to_crs(
    obj: dataset.GeodeticCoordRefSystem, crs: dataset.GeodeticCoordRefSystem,
    lla: Geodetic
) -> Geodetic:
    """
    Convert coordinates from one geodetic coordinate reference system to
    another.

    Args:
        obj (dataset.GeodeticCoordRefSystem): The source coordinate reference
            system.
        crs (dataset.GeodeticCoordRefSystem): The target coordinate reference
            system.
        lla (Geodetic): The coordinates to convert.

    Returns:
        Geodetic: The converted coordinates.
    """
    return geoid.lla_dat2dat(obj._struct_, crs._struct_, lla)


def to_wgs84(
    obj: dataset.GeodeticCoordRefSystem, lla: Geodetic
) -> Geodetic:
    """
    Convert coordinates from a geodetic coordinate reference system to WGS84.

    Args:
        obj (dataset.GeodeticCoordRefSystem): The source coordinate reference
            system.
        lla (Geodetic): The coordinates to convert.

    Returns:
        Geodetic: The converted coordinates in WGS84.
    """
    return geoid.lla_dat2dat(obj._struct_, WGS84._struct_, lla)


dataset.GeodeticCoordRefSystem.to_wgs84 = to_wgs84
dataset.GeodeticCoordRefSystem.to_crs = to_crs
dataset.Ellipsoid.distance = distance
dataset.Ellipsoid.destination = destination


class ProjectedCoordRefSystem(dataset.EpsgElement):
    """
    Coordinate reference system object allowing projection of geodetic
    coordinates to flat map (geographic coordinates).

    ```python
    >>> import epsglide
    >>> osgb36 = epsglide.ProjectedCoordRefSystem(27700)
    >>> london = epsglide.Geodetic(-0.127005, 51.518602, 0.)  # use degrees
    >>> osgb36(london)
    <metre:1.000[X=529939.106 Y=181680.962] alt=0.000>
    >>> osgb36.Projection
    {'Code': 19916, 'Name': 'British National Grid', 'href': 'https://apps.eps\
g.org/api/v1/Conversion/19916'}
    ```

    Attributes:
        GeodeticCoordRefSystem (dataset.GeodeticCoordRefSystem): geodetic
            reference system.
        Conversion (dataset.Conversion): projection method and parameters.
        CoordOperationMethod (dataset.CoordOperationMethod): projection
            description.
        CoordSystem (dataset.CoordSystem): 2D coordinate system and units.
        parameters (list): list of `dataset.CoordOperationParameter`.
    """

    def populate(self):
        self.GeodeticCoordRefSystem = dataset.GeodeticCoordRefSystem(
            self.BaseCoordRefSystem["Code"]
        )
        self._struct_ = dataset.src.Crs()
        self._struct_.datum = self.GeodeticCoordRefSystem._struct_

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
                ctypes.POINTER(Geodetic)
            ]
            self._proj_inverse = getattr(proj, f"{name}_inverse")
            self._proj_inverse.restype = Geodetic
            self._proj_inverse.argtypes = [
                ctypes.POINTER(dataset.src.Crs),
                ctypes.POINTER(Geographic)
            ]

    def __call__(
        self, element: typing.Union[Geodetic, Geographic]
    ) -> typing.Union[Geodetic, Geographic]:
        """
        """

        if isinstance(element, Geodetic):
            longitude = element.longitude + self._struct_.datum.prime.longitude
            lla = Geodetic(
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

    def forward(self, lla: Geodetic) -> Geographic:
        return self._proj_forward(self._struct_, lla)

    def inverse(self, xya: Geographic) -> Geodetic:
        return self._proj_inverse(self._struct_, xya)

    def transform(
        self, element: typing.Union[Geodetic, Geographic], dest_crs
    ) -> Geographic:
        """
        """
        lla = element if isinstance(element, Geodetic) else self(element)
        return dest_crs(geoid.lla_dat2da(self._struct, dest_crs._strut_, lla))


#######################
# loading C libraries #
#######################
# defining library name
__dll_ext__ = "dll" if sys.platform.startswith("win") else "so"
geoid = ctypes.CDLL(_get_file("geoid.%s" % __dll_ext__))
proj = ctypes.CDLL(_get_file("proj.%s" % __dll_ext__))

geoid.geocentric.argtypes = [
    ctypes.POINTER(dataset.src.Ellipsoid), ctypes.POINTER(Geodetic)
]
geoid.geocentric.restype = Geocentric

geoid.geodetic.argtypes = [
    ctypes.POINTER(dataset.src.Ellipsoid), ctypes.POINTER(Geocentric)
]
geoid.geodetic.restype = Geodetic

geoid.distance.argtypes = [
    ctypes.POINTER(dataset.src.Ellipsoid),
    ctypes.POINTER(Geodetic),
    ctypes.POINTER(Geodetic)
]
geoid.distance.restype = Vincenty_dist

geoid.destination.argtypes = [
    ctypes.POINTER(dataset.src.Ellipsoid),
    ctypes.POINTER(Geodetic),
    ctypes.POINTER(Vincenty_dist)
]
geoid.destination.restype = Vincenty_dest

geoid.lla_dat2dat.argtypes = [
    ctypes.POINTER(dataset.src.Datum),
    ctypes.POINTER(dataset.src.Datum),
    ctypes.POINTER(Geodetic)
]
geoid.lla_dat2dat.restype = Geodetic
