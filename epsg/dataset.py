# -*- encoding:utf-8 -*-

import os
import sys
import math
import json
import ctypes

import urllib.request
import urllib.error

from typing import Union

DATA = os.path.join(os.path.abspath(os.path.dirname(__file__)), ".dataset")

# alias table to translate https://apps.epsg.org/api/v1/Transformation
# parameter code to epsg.EpsgElement attribute name
TOWGS84_PARAMETER_CODES = {
    8605: "dx", 8606: "dy", 8607: "dz",
    8608: "rx", 8609: "ry", 8610: "rz",
    8611: "ds"
}

PROJ_METHOD_CODES = {
    1024: "merc", 1026: "merc", 1108: "merc", 9804: "merc", 9805: "merc",
    9659: "latlong",
    9807: "tmerc",
    9812: "omerc",
}

PROJ_PARAMETER_CODES = {
    8805: "k0",
    8801: "phi0",
    8802: "lambda0",
    8806: "x0",
    8807: "y0",
    8813: "azimuth",
    8823: "phi1",
    8824: "phi2",
}


class DatasetConnexionError(Exception):
    "to be raised when EPSG API is not available"


class DatasetNotFound(Exception):
    "to be raised when API call status code is not 200"


class DatasetIdentificationError(Exception):
    "to be raised when EpsgElement initialized with no info"


class DatumInitializationError(Exception):
    "to be raised when unmanaged datum parrameter occurs"


def _fetch(url: str) -> dict:
    try:
        resp = urllib.request.urlopen(url)
    except urllib.error.URLError:
        raise DatasetConnexionError("could not reach EPSG API server")
    status = resp.getcode()
    if status == 200:
        return json.loads(resp.read())
    else:
        raise DatasetNotFound(f"nothing found at {url} endpoint")


class EpsgElement(ctypes.Structure):
    """
    """

    @property
    def id(self) -> int:
        "return element `EPSG Code`."
        return self.__data["Code"]

    def __init__(self, code: int = None, name: str = None) -> None:
        if not any([code, name]):
            raise DatasetIdentificationError("epsg code or keyword is needed")

        if name:
            raise NotImplementedError("search by keyword not implemented yet")

        path = os.path.join(DATA, self.__class__.__name__, f"{code}.json")

        if os.path.exists(path):
            with open(path, "r") as in_:
                self.__data = json.load(in_)
        else:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            self.__data = _fetch(
                "https://apps.epsg.org/api/v1/" +
                f"{self.__class__.__name__}/{code}/"
            )
            with open(path, "w") as out:
                json.dump(self.__data, out, indent=2)

        for key, value in [
            item for item in self.__data.items() if item[-1] is not None
        ]:
            if hasattr(sys.modules[__name__], key):
                # create a new EpsgElement subclass
                setattr(
                    self, key,
                    getattr(sys.modules[__name__], key)(value.get("Code", 0))
                )

    def to_target(self, value: Union[int, float]) -> float:
        return value / self.Unit.ratio if hasattr(self, "Unit") else None

    def from_target(self, value: Union[int, float]) -> float:
        return value * self.Unit.ratio if hasattr(self, "Unit") else None

    def __getattr__(self, attr: str) -> Union[object, None]:
        try:
            return self.__data.get(attr)
        except KeyError:
            return ctypes.Structure.__getattr__(self, attr)


class Conversion(EpsgElement):
    ""


class CoordSystem(EpsgElement):
    ""


class CoordOperationMethod(EpsgElement):
    ""


class CoordOperationParameter(EpsgElement):
    ""


class Datum(EpsgElement):
    ""


class Unit(EpsgElement):
    _fields_ = [
        ("ratio", ctypes.c_double)
    ]

    def __init__(self, *a, **kw):
        EpsgElement.__init__(self, *a, **kw)
        self.ratio = self.FactorC / self.FactorB


class PrimeMeridian(EpsgElement):
    _fields_ = [
        ("longitude", ctypes.c_double)
    ]

    def __init__(self, *a, **kw):
        EpsgElement.__init__(self, *a, **kw)
        self.longitude = math.radians(self.GreenwichLongitude)


class Ellipsoid(EpsgElement):
    _fields_ = [
        ("a", ctypes.c_double),
        ("b", ctypes.c_double),
        ("e", ctypes.c_double),
        ("f", ctypes.c_double)
    ]

    def __init__(self, *a, **kw):
        EpsgElement.__init__(self, *a, **kw)
        self.a = self.SemiMajorAxis
        # initialize f, e and b values
        if self.InverseFlattening != 'NaN':
            self.f = 1. / self.InverseFlattening
            self.e = math.sqrt(2 * self.f - self.f**2)
            self.b = math.sqrt(self.a**2 * (1 - self.e**2))
        else:
            self.b = self.SemiMinorAxis
            self.f = (self.a - self.b) / self.a
            self.e = math.sqrt(2 * self.f - self.f**2)


class GeodeticCoordRefSystem(EpsgElement):
    _fields_ = [
        ("ellipsoid", Ellipsoid),
        ("prime", PrimeMeridian),
        ("ds", ctypes.c_double),
        ("dx", ctypes.c_double),
        ("dy", ctypes.c_double),
        ("dz", ctypes.c_double),
        ("rx", ctypes.c_double),
        ("ry", ctypes.c_double),
        ("rz", ctypes.c_double)
    ]

    def __init__(self, *a, **kw):
        EpsgElement.__init__(self, *a, **kw)
        self.ellipsoid = self.Datum.Ellipsoid
        self.prime = self.Datum.PrimeMeridian

        path = os.path.join(DATA, "ToWgs84", f"{self.id}.json")
        if os.path.exists(path):
            with open(path, "r") as in_:
                data = json.load(in_)
        else:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            results = _fetch(
                "https://apps.epsg.org/api/v1/Transformation/crs/" +
                f"?sourceCRSCode={self.id}&targetCRSCode=4326"
            ).get("Results", [])
            if results != []:
                data = _fetch(
                    "https://apps.epsg.org/api/v1/Transformation/" +
                    f"{results[0]['Code']}/"
                )
                with open(path, "w") as out:
                    json.dump(data, out, indent=2)
            else:
                raise Exception()

        for param in data["ParameterValues"]:
            try:
                setattr(
                    self, TOWGS84_PARAMETER_CODES[param["ParameterCode"]],
                    param["ParameterValue"]
                )
            except KeyError:
                raise DatumInitializationError(
                    f"unmanageable parameter {param['ParameterCode']}: "
                    f"{param['Name']}"
                )
