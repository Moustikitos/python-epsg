# -*- encoding:utf-8 -*-

import os
import sys
import math
import json
import webbrowser

import urllib.request
import urllib.error

from typing import Union
from epsglide import src

#: Path where json dataset are stored. On each EPSG dataset request, json data
#: are stored on this local path to allow introspection when needed and faster
#: execution.
DATA = os.path.join(os.path.abspath(os.path.dirname(__file__)), ".dataset")

# alias table to translate https://apps.epsg.org/api/v1/Transformation
# parameter code to epsg.EpsgElement attribute name
TOWGS84_PARAMETER_CODES = {
    8605: "dx", 8606: "dy", 8607: "dz",
    8608: "rx", 8609: "ry", 8610: "rz",
    8611: "ds"
}

# alias table to translate https://apps.epsg.org/api/v1/CoordOperationMethod
# parameter code to epsg.EpsgElement attribute name
PROJ_METHOD_CODES = {
    1024: "merc", 1026: "merc", 1108: "merc", 9804: "merc", 9805: "merc",
    9659: "latlong",
    9807: "tmerc",
    9812: "omerc",
    1102: "lcc", 1051: "lcc", 9801: "lcc", 9802: "lcc", 9803: "lcc",
    9822: "lcc"
}

# alias table to translate https://apps.epsg.org/api/v1/Conversion
# parameter code to epsg.EpsgElement attribute name
PROJ_PARAMETER_CODES = {
    8801: "phi0", 8802: "lambda0",
    8805: "k0", 8806: "x0", 8807: "y0",
    8813: "azimuth", 8823: "phi1", 8824: "phi2",
}


class DatasetConnexionError(Exception):
    """Exception raised when EPSG API is not available."""


class DatasetNotFound(Exception):
    """Exception raised when API call status code is not 200."""


class DatasetIdentificationError(Exception):
    """Exception raised when EpsgElement initialized with no info."""


class DatumInitializationError(Exception):
    """Exception raised when unmanageable datum parameter occurs."""


def _fetch(url: str) -> dict:
    try:
        resp = urllib.request.urlopen(url)
    except urllib.error.URLError as error:
        if error.code == 404:
            raise DatasetNotFound(error.reason)
        else:
            raise DatasetConnexionError("could not reach EPSG API server")
    else:
        return json.loads(resp.read())


# class EpsgElement(ctypes.Structure):
class EpsgElement(object):
    """
    Represents an EPSG dataset element.

    Attributes:
        _struct_ (ctypes.Structure): object representing the structure of the
            equivalant C element.

    Arguments:
        code (int): the EPSG code of the element.
        name (str): the name of the element.

    Raises:
        DatasetIdentificationError: if either EPSG code or name is not
            provided.
        NotImplementedError: if searching by keyword is attempted (not
            implemented yet).
    """

    _struct_: src.ctypes.Structure = None
    id: int = None

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
                "https://apps.epsg.org/api/v1/"
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

    def __repr__(self):
        """
        Return a string representation of the `EpsgElement` object.

        Returns:
            str: a string representation of the object in the format
                `<ClassName Code: Name>`.
        """
        return f"<{self.__class__.__name__} {self.Code}: {self.Name}>"

    def __getattr__(self, attr: str) -> Union[object, None]:
        try:
            return getattr(object.__getattribute__(self, "_struct_"), attr)
        except AttributeError:
            try:
                return self.__data[attr]
            except KeyError:
                return object.__getattribute__(self, attr)

    def browse(self) -> None:
        lnk = [e for e in self.Links if e.get("rel", None) == "self"]
        if lnk:
            webbrowser.open(lnk[0].get("href"))

    def populate(self):
        """
        Populate the EPSG dataset element. This method is meant to be
        overridden by subclasses.
        """
        pass


class Unit(EpsgElement):
    """
    Represents a unit in EPSG dataset.

    Attributes:
        ratio (float): The ratio value of the unit.
    """

    def populate(self):
        self._struct_ = src.Unit()
        if self.FactorB != 0:
            self._struct_.ratio = self.FactorC / self.FactorB
        else:
            self._struct_.ratio = 1

    def from_target(self, value: Union[int, float]) -> float:
        """
        Convert a value to the dataset specific unit.

        ```python
        >>> u = epsglide.dataset.Unit(9003)
        >>> u
        <Unit 9003: US survey foot>
        >>> u.from_target(1) # convert one metre into US survey foot
        3.2808333333333333
        ```

        Arguments:
            value (int|float): the value to be converted.

        Returns:
            float|None: the converted value, or None if no conversion is
                possible.
        """
        return value * self.ratio

    def to_target(self, value: Union[int, float]) -> float:
        """
        Convert a value to computation specific units.

        ```python
        >>> u = epsglide.dataset.Unit(9002)
        >>> u
        <Unit 9002: foot>
        >>> u.to_target(1) # convert one international feet into meters
        0.3048
        ```

        Arguments:
            value (int|float): the value to be converted.

        Returns:
            float|None: the converted value, or None if no conversion is
                possible.
        """
        return value / self.ratio


class PrimeMeridian(EpsgElement):
    """
    Represents a prime meridian in EPSG dataset.

    Attributes:
        longitude (float): The longitude value of the prime meridian.
    """

    def populate(self):
        self._struct_ = src.Prime()
        self._struct_.longitude = math.radians(self.GreenwichLongitude)


class Ellipsoid(EpsgElement):
    """
    Represents an ellipsoid model used in geodetic coordinate reference
    systems.

    Methods:
        populate: Populate the `Ellipsoid` object with necessary data,
            including parameters related to its shape and size.
    """

    def populate(self):
        """
        Populate the `Ellipsoid` object with necessary data.

        This method initializes the internal structure (`_struct_`) of the
        `Ellipsoid` object with information about its semi-major axis,
        semi-minor axis, flattening, eccentricity, and other related
        parameters.

        The initialization process depends on whether the ellipsoid's
        inverse flattening is provided or calculated from its semi-major
        and semi-minor axes.
        """
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
    """
    Represents a geodetic coordinate reference system.

    Methods:
        populate: Populate the GeodeticCoordRefSystem object with necessary
            data, including datum and transformation parameters.
    """

    def populate(self):
        """
        Populate the `GeodeticCoordRefSystem` object with necessary data.

        This method initializes the internal structure (`_struct_`) of the
        `GeodeticCoordRefSystem` object with information about the datum,
        ellipsoid, prime meridian, and transformation parameters.

        Raises:
            DatasetNotFound: If no transformation is found for the given
                coordinate reference system (CRS) code.
            DatumInitializationError: If an unmanageable transformation
                parameter is encountered during initialization.
        """
        self._struct_ = src.Datum()
        self._struct_.ellipsoid = self.Datum.Ellipsoid._struct_
        self._struct_.prime = self.Datum.PrimeMeridian._struct_

        if self.id == 4326:
            return

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
                raise DatasetNotFound("No transformation found.")

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


# class are defined here only to allow EPSG element tree.
class Conversion(EpsgElement):
    pass


class CoordSystem(EpsgElement):
    pass


class CoordOperationMethod(EpsgElement):
    pass


class CoordOperationParameter(EpsgElement):
    pass


class Datum(EpsgElement):
    pass
