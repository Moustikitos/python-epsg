# -*- encoding:utf-8 -*-

import ctypes


class Unit(ctypes.Structure):
    _fields_ = [("ratio", ctypes.c_double)]


class Prime(ctypes.Structure):
    _fields_ = [("longitude", ctypes.c_double)]


class Ellipsoid(ctypes.Structure):
    _fields_ = [
        ("a", ctypes.c_double),
        ("b", ctypes.c_double),
        ("e", ctypes.c_double),
        ("f", ctypes.c_double)
    ]


class Datum(ctypes.Structure):
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
