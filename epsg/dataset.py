# -*- encoding:utf-8 -*-

import os
import sys
import json
import ctypes

import urllib.request
import urllib.error

TOWGS84_PARAMETER_CODES = {
    8605: "dx", 8606: "dy", 8607: "dz",
    8608: "rx", 8609: "ry", 8610: "rz",
    8611: "ds"
}

DATA = os.path.join(os.path.abspath(os.path.dirname(__file__)), ".dataset")


def _fetch(url):
    try:
        resp = urllib.request.urlopen(url)
    except urllib.error.URLError:
        raise Exception()
    status = resp.getcode()
    if status == 200:
        return json.loads(resp.read())
    else:
        raise Exception()


class EpsgElement(ctypes.Structure):
    _fields_ = []

    @property
    def id(self):
        return self.__data["Code"]

    def __init__(self, code: int = None, name: str = None) -> None:
        if not any([code, name]):
            raise Exception()

        if name:
            raise NotImplementedError()

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

    def __getattr__(self, attr):
        try:
            return self.__data.get(attr)
        except KeyError:
            return ctypes.Structure.__getattr__(self, attr)


class Unit(EpsgElement):
    pass


class PrimeMeridian(EpsgElement):
    _fields_ = [
        ("longitude", ctypes.c_double)
    ]

    def __init__(self, *a, **kw):
        EpsgElement.__init__(self, *a, **kw)
        self.a = self.GreenwichLongitude


class Ellipsoid(EpsgElement):
    _fields_ = [
        ("a", ctypes.c_double),
        ("f", ctypes.c_double)
    ]

    def __init__(self, *a, **kw):
        EpsgElement.__init__(self, *a, **kw)
        self.a = self.SemiMajorAxis
        try:
            self.f = 1. / self.InverseFlattening
        except TypeError:
            # if InverseFlattening = 'NaN'
            self.f = (self.a - self.SemiMinorAxis) / self.a


class Datum(EpsgElement):
    pass


class GeodeticCoordRefSystem(EpsgElement):
    _fields_ = [
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
        self.datum = self.Datum
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
            setattr(
                self, TOWGS84_PARAMETER_CODES[param["ParameterCode"]],
                param["ParameterValue"]
            )
