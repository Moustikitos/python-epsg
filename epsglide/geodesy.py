# -*- encoding:utf-8 -*-

"""
Module for handling geodetic coordinates and their representations.

This module provides functionality for working with geodetic coordinates,
allowing for different representations and initialization methods.

Supported representations:

  - [x] Maidenhead
  - [x] Geohash
  - [x] Georef
  - [x] GARS

Even if angular value are stored in radians, initialisation and
representation are done using degrees. `Geodetic` class can be imported
from `geodesy` package module:

    >>> from epsglide.geodesy import Geodetic
    >>> dublin = Geodetic(-6.272877, 53.344606, 105.)  # use degrees
    >>> london = Geodetic(-0.127005, 51.518602, 0.)  # use degrees
    >>> dublin  # show degrees in dms format
    <lon=-6.272877 lat=53.344606 alt=105.000>
    >>> london  # show degrees in dms format
    <lon=-000d07m37.21800s lat=+051d31m6.96720s alt=0.0>
    >>> london.longitude  # value is stored in radians
    -0.002216655416495398
"""

import io
import math
import ctypes

from urllib.request import urlopen

_TORAD = math.pi / 180.0
_TODEG = 180.0 / math.pi


def _dms(value):
    if value == 0:
        return f"{0:03d}°{0:02d}'{0.0:.5f}\""

    s = -1 if value < 0 else 1
    value = abs(value)
    degrees = math.floor(value)
    value = (value - degrees) * 60
    minutes = int(math.floor(value))
    secondes = (value - minutes) * 60

    if round(secondes, 3) == 60:
        minutes += 1
        secondes = 0
        if round(minutes, 5) == 60:
            degrees += 1
            minutes = 0

    return \
        f"{'+' if s > 0 else '-'}{degrees:03d}d{minutes:02d}m{secondes:.5f}s"


class Geodetic(ctypes.Structure):
    """
    `ctypes` structure for geodetic coordinates. This class also provides
    various standart initialization from various representation such as
    `maidenhead`, `georef`, `geohash`.

    ```python
    >>> Geodetic.from_maidenhead('IO91wm44sl21gl14kb51om')  # london
    <lon=-000d07m37.21800s lat=+051d31m6.96720s alt=0.0>
    >>> epsglide.Geodetic.from_georef('MKQG52883162')  # london
    <lon=-000d07m36.90000s lat=+051d31m7.50000s alt=0.0>
    >>> Geodeis.from_geohash('gcpvj4et8e6pwdj0ft1k', center=True)  # london
    <lon=-000d07m37.21800s lat=+051d31m6.96720s alt=0.0>
    ```

    The associated GARS area (5minx5min tile) can also be provided.
    ```python
    >>> london.gars()
    '360MV46'
    ```

    Attributes:
        longitude (float): longitude value of geodetic coordinates in radians.
        latitude (float): latitude value of geodetic coordinates in radians.
        altitude (float): elevation of the geodetic coordinates in meters.
    """
    _fields_ = [
        ("longitude", ctypes.c_double),
        ("latitude", ctypes.c_double),
        ("altitude", ctypes.c_double)
    ]

    def __init__(self, *args, **kwargs) -> None:
        args = list(args)
        for i in range(min(2, len(args))):
            args[i] *= _TORAD
        for key in [k for k in kwargs if k in ["longitude", "latitude"]]:
            kwargs[key] *= _TORAD
        ctypes.Structure.__init__(self, *args, **kwargs)

    def __repr__(self) -> str:
        return \
            f"<lon={_dms(self.longitude * _TODEG)} " +\
            f"lat={_dms(self.latitude * _TODEG)} " +\
            f"alt={self.altitude:.3f}>"

    def maidenhead(self, level: int = 4) -> str:
        """
        Convert coordinates to maidenhead representation. Precision can be set
        using `level` parameter.

        ```python
        >>> dublin.maidenhead()
        'IO63ui72gq'
        >>> dublin.maidenhead(level=6)
        'IO63ui72gq19dh'
        ```

        Arguments:
            level (int): precision level of maidenhead.
        Returns:
            str: Maidenhead string.
        """
        base = "ABCDEFGHIJKLMNOPQRSTUVWX"
        longitude = (self.longitude * _TODEG + 180) % 360
        latitude = (self.latitude * _TODEG + 90) % 180

        result = ""

        lon_idx = longitude / 20
        lat_idx = latitude / 10
        result += \
            base[int(math.floor(lon_idx))] + \
            base[int(math.floor(lat_idx))]

        coef = 10.
        for i in range(level):
            lon_idx = (lon_idx - math.floor(lon_idx)) * coef
            lat_idx = (lat_idx - math.floor(lat_idx)) * coef
            if coef == 10.:
                result += "%d%d" % (math.floor(lon_idx), math.floor(lat_idx))
            else:
                result += (
                    base[int(math.floor(lon_idx))] +
                    base[int(math.floor(lat_idx))]
                ).lower()
            coef = 24. if coef == 10. else 10.

        return result

    @staticmethod
    def from_maidenhead(maidenhead: str):
        """
        Return Geodetic object from maidenhead string.

        Arguments:
            maidenhead (str): maidenhead representation.
        Returns:
            epsglide.Geodetic: geodetic coordinates.

            A `precision` tuple (longitude, latitude) in degrees is added as
            class attribute.

        ```python
        >>> Geodetic.from_maidenhead('IO63ui72gq').precision
        (0.00015624999999999998, 0.00015624999999999998)
        >>> Geodetic.from_maidenhead('IO63ui72gq19dh').precision
        (6.510416666666665e-07, 6.510416666666665e-07)
        ```
        """
        base = "ABCDEFGHIJKLMNOPQRSTUVWX"
        longitude = latitude = 0
        eps = 18./2.
        lon_str = list(reversed(maidenhead[0::2].upper()))
        lat_str = list(reversed(maidenhead[1::2].upper()))

        for i, j in zip(lon_str[:-1], lat_str[:-1]):
            if i in "0123456789":
                longitude = (longitude + int(i)) / 10.
                latitude = (latitude + int(j)) / 10.
                eps /= 10.
            else:
                longitude = (longitude + base.index(i)) / 24.
                latitude = (latitude + base.index(j)) / 24.
                eps /= 24.

        longitude = (longitude + base.index(lon_str[-1])) * 20. + eps
        latitude = (latitude + base.index(lat_str[-1])) * 10. + eps

        result = Geodetic(longitude=longitude-180, latitude=latitude-90)
        setattr(result, "precision", (eps, eps))
        return result

    def georef(self, digit: int = 8) -> str:
        """
        Convert coordinates to georef. Best precision can be set with a
        maximul of 8 digit (default). With this level, the precision is about
        8.3e-05 degrees in longitude and latitude.

        ```python
        >>> dublin.georef()
        'MKJJ43322037'
        >>> dublin.georef(digit=6)
        'MKJJ433203'
        ```

        Arguments:
            digit (int): digit number of georef (can be 4, 6 or 8).
        Returns:
            str: georef representation.
        """
        base = "ABCDEFGHJKLMNPQRSTUVWXYZ"
        longitude = (self.longitude * _TODEG + 180) % 360
        latitude = (self.latitude * _TODEG + 90) % 180

        result = ""

        lon_idx = longitude / 15.
        lat_idx = latitude / 15.
        result += \
            base[int(math.floor(lon_idx))] + \
            base[int(math.floor(lat_idx))]

        lon_idx = (lon_idx - math.floor(lon_idx)) * 15.
        lat_idx = (lat_idx - math.floor(lat_idx)) * 15.
        result += \
            base[int(math.floor(lon_idx))] + \
            base[int(math.floor(lat_idx))]

        lon_idx = (lon_idx - math.floor(lon_idx)) * 60.
        lat_idx = (lat_idx - math.floor(lat_idx)) * 60.

        lon = "%02d" % lon_idx
        lat = "%02d" % lat_idx

        if digit == 6:
            lon_idx = 10 - (lon_idx - math.floor(lon_idx)) * 10.
            lat_idx = 10 - (lat_idx - math.floor(lat_idx)) * 10.
            lat += "%01d" % math.floor(lon_idx)
            lon += "%01d" % math.floor(lat_idx)
        elif digit == 8:
            lon_idx = 100 - (lon_idx - math.floor(lon_idx)) * 100.
            lat_idx = 100 - (lat_idx - math.floor(lat_idx)) * 100.
            lat += "%02d" % math.floor(lon_idx)
            lon += "%02d" % math.floor(lat_idx)

        return result + lon + lat

    @staticmethod
    def from_georef(georef: str):
        """
        Return Geodetic object from georef.

        ```python
        >>> Geodetic.from_georef('MKJJ433220')
        <lon=-006d15m57.000s lat=+053d22m45.000s alt=0.000>
        >>> Geodetic.from_georef('MKJJ43322037')
        <lon=-006d16m21.900s lat=+053d20m41.100s alt=0.000>
        ```

        Arguments:
            georef (str): georef representation.
        Returns:
            epsglide.Geodetic: geodetic coordinates.

            A `precision` tuple (longitude, latitude) in degrees is added as
            class attribute.

        ```python
        >>> epsglide.Geodetic.from_georef('MKJJ433220').precision   
        (0.0008333333333333333, 0.0008333333333333333)
        >>> Geodetic.from_georef('MKJJ43322037').precision
        (8.333333333333333e-05, 8.333333333333333e-05)
        ```
        """
        base = "ABCDEFGHJKLMNPQRSTUVWXYZ"
        eps = 1./2./60.

        if len(georef) == 12:
            longitude = (1-int(georef[10:])/100. + int(georef[4:6]))/60.
            latitude = (1-int(georef[6:8])/100. + int(georef[8:10]))/60.
            eps /= 100.
        elif len(georef) == 10:
            longitude = (1-int(georef[9])/10. + int(georef[4:6]))/60.
            latitude = (1-int(georef[6])/10. + int(georef[7:9]))/60.
            eps /= 10.
        else:
            longitude = int(georef[4:6])/60.
            latitude = int(georef[6:])/60.

        longitude = (
            (longitude + base.index(georef[2])) / 15. + base.index(georef[0])
        ) * 15. + eps
        latitude = (
            (latitude + base.index(georef[3])) / 15. + base.index(georef[1])
        ) * 15. + eps

        result = Geodetic(longitude=longitude - 180, latitude=latitude - 90)
        setattr(result, "precision", (eps, eps))
        return result

    def gars(self) -> str:
        """
        Get the associated GARS Area (5minx5min tile).

        ```python
        >>> dublin.gars()
        '348MY16'
        ```
        """
        base = "ABCDEFGHJKLMNPQRSTUVWXYZ"
        longitude = (self.longitude*_TODEG+180) % 360
        latitude = (self.latitude*_TODEG+90) % 180

        lon_idx = longitude / 0.5
        lat_idx = latitude / 0.5

        quadrant = \
            "%03d" % (lon_idx+1) + \
            base[int(math.floor(lat_idx // 24))] + \
            base[int(math.floor(lat_idx % 24))]

        lon_num_idx = (lon_idx - math.floor(lon_idx)) * 2.
        lat_num_idx = (lat_idx - math.floor(lat_idx)) * 2.
        j = math.floor(lon_num_idx)
        i = 1-math.floor(lat_num_idx)
        number = i*(j+1)+j+1

        lon_key_idx = (lon_num_idx - math.floor(lon_num_idx)) * 3.
        lat_key_idx = (lat_num_idx - math.floor(lat_num_idx)) * 3.
        j = math.floor(lon_key_idx)
        i = 2-math.floor(lat_key_idx)
        key = i*(j+1)+j+1

        return quadrant + str(number) + str(key)

    @staticmethod
    def from_gars(gars: str, anchor: str = ""):
        """
        Return Geodetic object from gars. Optional anchor value to define
        where to handle 5minx5min tile.

        ```python
        >>> Geodetic.from_gars('348MY16', anchor="nw")
        <lon=-006d20m0.000s lat=+053d25m0.000s alt=0.000>
        >>> epsg.Geodetic.from_gars('348MY16')
        <lon=-006d17m30.000s lat=+053d22m30.000s alt=0.000>
        ```

        Arguments:
            gars (str): gars representation.
            anchor (str): tile anchor using `n`, `e`, `s` or `w`.
        Returns:
            epsglide.Geodetic: geodetic coordinates.

            Global precision of centered GARS coordinates is about `0.0833`
            degrees in longitude ad latitude.
        """
        base = "ABCDEFGHJKLMNPQRSTUVWXYZ"
        longitude = 5. / 60. * (
            0 if "w" in anchor else 1 if "e" in anchor else 0.5
        )
        latitude = 5. / 60. * (
            0 if "s" in anchor else 1 if "n" in anchor else 0.5
        )

        key = gars[6]
        longitude += 5. / 60. * (
            0 if key in "147" else 1 if key in "258" else 2
        )
        latitude += 5. / 60. * (
            0 if key in "789" else 1 if key in "456" else 2
        )

        number = gars[5]
        longitude += 15. / 60. * (0 if number in "13" else 1)
        latitude += 15. / 60. * (0 if number in "34" else 1)

        longitude += (int(gars[:3])-1) * 0.5
        latitude += (base.index(gars[3]) * 24 + base.index(gars[4])) * 0.5

        result = Geodetic(longitude=longitude - 180, latitude=latitude - 90)
        setattr(result, "precision", (5./60/2, 5./60/2))
        return result

    def geohash(
            self, digit: int = 10,
            base: str = "0123456789bcdefghjkmnpqrstuvwxyz"
    ) -> str:
        """
        Convert coordinates to geohash. Precision can be set using `digit`
        parameter.

        ```python
        >>> london.geohash()
        'gcpvj4et8e'
        ```

        Arguments:
            digit (int): digit number of geohash [default: 10].
            base (str): a 32-sized string of unique caracter. Same base should
                be used to decode correctly the geohash.
        Returns:
            str: geohash representation.
        """
        min_lon, max_lon = -180., 180.
        min_lat, max_lat = -90., 90.
        mid_lon, mid_lat = 0., 0.

        longitude = math.degrees(self.longitude)
        latitude = math.degrees(self.latitude)

        geohash = ""
        even = False
        while len(geohash) < digit:
            val = 0
            for mask in [0b10000, 0b01000, 0b00100, 0b00010, 0b00001]:
                if not even:
                    if longitude >= mid_lon:
                        min_lon = mid_lon
                        val = mask if val == 0 else val | mask
                    else:
                        max_lon = mid_lon
                    mid_lon = (min_lon + max_lon) / 2
                else:
                    if latitude >= mid_lat:
                        min_lat = mid_lat
                        val = mask if val == 0 else val | mask
                    else:
                        max_lat = mid_lat
                    mid_lat = (min_lat + max_lat) / 2
                even = not even
            geohash += base[val]
        return geohash

    @staticmethod
    def from_geohash(
        geohash: str, base: str = "0123456789bcdefghjkmnpqrstuvwxyz",
        center: bool = True
    ):
        """
        Return Geodetic object from geohash.

        ```python
        >>> Geodetic.from_geohash('gcpvj4et8e')
        <lon=-000d07m37.19969s lat=+051d31m6.97229s alt=0.0>
        ```

        Arguments:
            base (str): a 32-sized string of unique caracter used to encode the
                geodetic coordinates.
        Returns:
            epsglide.Geodetic: geodetic coordinates.

            A `precision` tuple (longitude, latitude) in degrees is added as
            class attribute.

        ```python
        >>> epsglide.Geodetic.from_geohash('gcpvj4et8e').precision
        (2.682209014892578e-06, 1.341104507446289e-06)
        ```
        """
        eps_lon, eps_lat = 360./2., 180./2.
        min_lon, max_lon = -180., 180.
        min_lat, max_lat = -90., 90.
        mid_lon, mid_lat = 0., 0.

        even = False
        for digit in geohash:
            val = base.index(digit)
            for mask in [0b10000, 0b01000, 0b00100, 0b00010, 0b00001]:
                if not even:
                    if mask & val == mask:
                        min_lon = mid_lon
                    else:
                        max_lon = mid_lon
                    mid_lon = (min_lon+max_lon)/2.
                    eps_lon /= 2.
                else:
                    if mask & val == mask:
                        min_lat = mid_lat
                    else:
                        max_lat = mid_lat
                    mid_lat = (min_lat+max_lat)/2.
                    eps_lat /= 2.
                even = not even

        if center:
            mid_lon += eps_lon/2
            mid_lat += eps_lat/2

        result = Geodetic(mid_lon, mid_lat)
        setattr(result, "precision", (eps_lon/2, eps_lat/2))
        return result

    def url_load_location(self, url, **kwargs):
        """
        Return a static map image data from map provider.

        ```python
        >>> # below a mapbox-static-map url centered on [lon, lat] with a red
        >>> # pin, width, height and zoom to be specified on call
        >>> url = "https://api.mapbox.com/styles/v1/mapbox/outdoors-v11/static"
        ... "/pin-s+f74e4e(%(lon)f,%(lat)f)/%(lon)f,%(lat)f,%(zoom)d,0"
        ... "/%(width)dx%(height)d?access_token=%(token)s"
        >>> data = dublin.url_load_location(
        ...    url, zoom=15, width=600, height=400, token="xx-xxxxxx-xx"
        ... )
        >>> # see `epsg.geodesy.Geodetic.dump_location`
        >>> with io.open("dump.png", "wb") as f:
        ...    f.write(data)
        ```

        Arguments:
            url (str): map provider url containing `%(lon)f` and `%(lat)f`
                format expression to be replaced by longitude and latitude in
                the proper unit according to map provider.
            **kwargs (dict): key-value pairs to match entries in url according
                to python string formatting.
        Returns:
            Image data as `bytes` (py3) or `str` (py2).
        """
        kwargs.update(
            lon=self.longitude * _TODEG,
            lat=self.latitude * _TODEG
        )
        try:
            opener = urlopen(url % kwargs)
        except Exception as error:
            print("%r" % error)
        else:
            return opener.read()

    def dump_location(self, name, url, **kwargs):
        """
        Dump a static map image from map provider into filesystem.

        Arguments:
            name (str): a valid filepath.
            url (str): map provider url containing `%(lon)f` and `%(lat)f`
                format expression to be replaced by longitude and latitude
                found in GPS data.
            **kwargs (dict): key-value pairs to match entries in url according
                to python string formatting.
        """
        with io.open(name, "wb") as fileobj:
            fileobj.write(self.url_load_location(url, **kwargs))
