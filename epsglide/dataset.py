# -*- encoding:utf-8 -*-

import os
import sys
import math
import json

import urllib.request
import urllib.error

from typing import Union
from epsglide import src

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
    1102: "lcc", 1051: "lcc", 9801: "lcc", 9802: "lcc", 9803: "lcc",
    9822: "lcc"
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
    "to be raised when unmanageable datum parrameter occurs"


def _fetch(url: str) -> dict:
    try:
        resp = urllib.request.urlopen(url)
    except urllib.error.URLError as error:
        if error.code == 404:
            raise DatasetNotFound(error.reason)
        else:
            raise DatasetConnexionError("could not reach EPSG API server")
    # status = resp.getcode()
    # if status == 200:
    return json.loads(resp.read())
    # else:
    #     raise DatasetNotFound(f"nothing found at {url} endpoint")


# class EpsgElement(ctypes.Structure):
class EpsgElement(object):
    """
    """

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

        self.id = self.__data["Code"]
        for key, value in [
            item for item in self.__data.items() if item[-1] is not None
        ]:
            if hasattr(sys.modules[__name__], key):
                # create a new EpsgElement subclass
                setattr(
                    self, key,
                    getattr(sys.modules[__name__], key)(value.get("Code", 0))
                )

        self.populate()

    def populate(self):
        pass

    def to_target(self, value: Union[int, float]) -> float:
        return value / self.Unit.ratio if hasattr(self, "Unit") else None

    def from_target(self, value: Union[int, float]) -> float:
        return value * self.Unit.ratio if hasattr(self, "Unit") else None

    def __repr__(self):
        return f"<{self.__class__.__name__} #{self.Code}: {self.Name}>"

    def __getattr__(self, attr: str) -> Union[object, None]:
        try:
            return getattr(object.__getattribute__(self, "_struct_"), attr)
        except AttributeError:
            try:
                return self.__data[attr]
            except KeyError:
                return object.__getattribute__(self, attr)


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

    def populate(self):
        self._struct_ = src.Unit()
        self._struct_.ratio = self.FactorC / self.FactorB


class PrimeMeridian(EpsgElement):

    def populate(self):
        self._struct_ = src.Prime()
        self._struct_.longitude = math.radians(self.GreenwichLongitude)


class Ellipsoid(EpsgElement):

    def populate(self):
        self._struct_ = src.Ellipsoid()
        self._struct_.a = self.SemiMajorAxis
        # initialize f, e and b values
        if self.InverseFlattening != 'NaN':
            self._struct_.f = 1. / self.InverseFlattening
            self._struct_.e = \
                math.sqrt(2 * self._struct_.f - self._struct_.f**2)
            self._struct_.b = \
                math.sqrt(self._struct_.a**2 * (1 - self._struct_.e**2))
        else:
            self._struct_.b = self.SemiMinorAxis
            self._struct_.f = \
                (self._struct_.a - self._struct_.b) / self._struct_.a
            self._struct_.e = \
                math.sqrt(2 * self._struct_.f - self._struct_.f**2)


class GeodeticCoordRefSystem(EpsgElement):

    def populate(self):
        self._struct_ = src.Datum()
        self._struct_.ellipsoid = self.Datum.Ellipsoid._struct_
        self._struct_.prime = self.Datum.PrimeMeridian._struct_

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
                    self._struct_,
                    TOWGS84_PARAMETER_CODES[param["ParameterCode"]],
                    param["ParameterValue"]
                )
            except KeyError:
                raise DatumInitializationError(
                    f"unmanageable parameter {param['ParameterCode']}: "
                    f"{param['Name']}"
                )
