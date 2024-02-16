# -*- coding:utf-8 -*-

import os
import sys
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext


#: to build a pure .so or .dll file to be used within ctypes
class CTypes(Extension):
    pass


class build_ctypes_ext(build_ext):

    def get_libraries(self, ext):
        self._ctypes = isinstance(ext, CTypes)
        return super().get_libraries(ext)

    def build_extension(self, ext):
        self._ctypes = isinstance(ext, CTypes)
        return super().build_extension(ext)

    def get_export_symbols(self, ext):
        if self._ctypes:
            return ext.export_symbols
        return super().get_export_symbols(ext)

    def get_ext_filename(self, ext_name):
        if getattr(self, "_ctypes", False):
            return ext_name.replace(".", os.sep) + (
                '.dll' if sys.platform.startswith("win") else '.so'
            )
        return super().get_ext_filename(ext_name)


version = open("./VERSION", "r")
long_description = open("./README.md", "r")

kw = {
    "version": version.read().strip(),
    "name": "EPSGlide",
    "keywords": [
        "epsg", "projection", "great", "circle", "geohash", "georef", "GARS",
        "maidenhead", "dataset"
    ],
    "author": "Bruno THOORENS",
    "author_email": "moustikitos@gmail.com",
    "maintainer": "Bruno THOORENS",
    "maintainer_email": "moustikitos@gmail.com",
    "url": "https://github.com/Moustikitos/python-epsg",
    # "download_url": "TODO",
    "description":
        "Efficient great circle computation and projection library "
        "with access to EPSG dataset public API",
    "long_description": long_description.read(),
    "long_description_content_type": "text/markdown",
    "packages": ["epsglide"],
    "include_package_data": True,
    "ext_modules": [
        CTypes(
            'epsglide.geoid',
            extra_compile_args=[],
            include_dirs=['src/'],
            sources=[
                "src/geoid.c"
            ]
        ),
        CTypes(
            'epsglide.proj',
            extra_compile_args=[],
            include_dirs=['src/'],
            sources=[
                "src/tmerc.c",
                "src/miller.c",
                "src/eqc.c",
                "src/merc.c",
                "src/lcc.c"
            ]
        )
    ],
    "cmdclass": {"build_ext": build_ctypes_ext},
    "license": "Copyright 2024, THOORENS Bruno, BSD licence",
    "classifiers": [
        "Development Status :: 3 - Alpha",
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: C',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering :: GIS',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
}

long_description.close()
version.close()

setup(**kw)
