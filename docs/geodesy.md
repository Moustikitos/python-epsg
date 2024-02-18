<a id="epsglide.geodesy"></a>

# epsglide.geodesy

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

<a id="epsglide.geodesy.Geodetic"></a>

## Geodetic Objects

```python
class Geodetic(ctypes.Structure)
```

`ctypes` structure for geodetic coordinates. This class also provides
various standart initialization from various representation such as
`maidenhead`, `georef`, `geohash`.


The associated GARS area (5minx5min tile) can also be provided.

```python
>>> Geodetic.from_maidenhead('IO91wm44sl21gl14kb51om')  # london
<lon=-000d07m37.21800s lat=+051d31m6.96720s alt=0.0>
>>> epsglide.Geodetic.from_georef('MKQG52883162')  # london
<lon=-000d07m36.90000s lat=+051d31m7.50000s alt=0.0>
>>> Geodeis.from_geohash('gcpvj4et8e6pwdj0ft1k', center=True)  # london
<lon=-000d07m37.21800s lat=+051d31m6.96720s alt=0.0>
```
```python
>>> london.gars()
'360MV46'
```

**Attributes**:

- `longitude` _float_ - longitude value of geodetic coordinates in radians.
- `latitude` _float_ - latitude value of geodetic coordinates in radians.
- `altitude` _float_ - elevation of the geodetic coordinates in meters.

<a id="epsglide.geodesy.Geodetic.maidenhead"></a>

#### maidenhead

```python
def maidenhead(level: int = 4) -> str
```

Convert coordinates to maidenhead representation. Precision can be set
using `level` parameter.


```python
>>> dublin.maidenhead()
'IO63ui72gq'
>>> dublin.maidenhead(level=6)
'IO63ui72gq19dh'
```

**Arguments**:

- `level` _int_ - precision level of maidenhead.

**Returns**:

- `str` - Maidenhead string.

<a id="epsglide.geodesy.Geodetic.from_maidenhead"></a>

#### from\_maidenhead

```python
@staticmethod
def from_maidenhead(maidenhead: str)
```

Return Geodetic object from maidenhead string.

**Arguments**:

- `maidenhead` _str_ - maidenhead representation.

**Returns**:

- `epsglide.Geodetic` - geodetic coordinates.
  
  A `precision` tuple (longitude, latitude) in degrees is added as
  class attribute.
  
```python
>>> Geodetic.from_maidenhead('IO63ui72gq').precision
(0.00015624999999999998, 0.00015624999999999998)
>>> Geodetic.from_maidenhead('IO63ui72gq19dh').precision
(6.510416666666665e-07, 6.510416666666665e-07)
```

<a id="epsglide.geodesy.Geodetic.georef"></a>

#### georef

```python
def georef(digit: int = 8) -> str
```

Convert coordinates to georef. Best precision can be set with a
maximul of 8 digit (default). With this level, the precision is about
8.3e-05 degrees in longitude and latitude.


```python
>>> dublin.georef()
'MKJJ43322037'
>>> dublin.georef(digit=6)
'MKJJ433203'
```

**Arguments**:

- `digit` _int_ - digit number of georef (can be 4, 6 or 8).

**Returns**:

- `str` - georef representation.

<a id="epsglide.geodesy.Geodetic.from_georef"></a>

#### from\_georef

```python
@staticmethod
def from_georef(georef: str)
```

Return Geodetic object from georef.


```python
>>> Geodetic.from_georef('MKJJ433220')
<lon=-006d15m57.000s lat=+053d22m45.000s alt=0.000>
>>> Geodetic.from_georef('MKJJ43322037')
<lon=-006d16m21.900s lat=+053d20m41.100s alt=0.000>
```

**Arguments**:

- `georef` _str_ - georef representation.

**Returns**:

- `epsglide.Geodetic` - geodetic coordinates.
  
  A `precision` tuple (longitude, latitude) in degrees is added as
  class attribute.
  
```python
>>> epsglide.Geodetic.from_georef('MKJJ433220').precision   
(0.0008333333333333333, 0.0008333333333333333)
>>> Geodetic.from_georef('MKJJ43322037').precision
(8.333333333333333e-05, 8.333333333333333e-05)
```

<a id="epsglide.geodesy.Geodetic.gars"></a>

#### gars

```python
def gars() -> str
```

Get the associated GARS Area (5minx5min tile).

```python
>>> dublin.gars()
'348MY16'
```

<a id="epsglide.geodesy.Geodetic.from_gars"></a>

#### from\_gars

```python
@staticmethod
def from_gars(gars: str, anchor: str = "")
```

Return Geodetic object from gars. Optional anchor value to define
where to handle 5minx5min tile.


```python
>>> Geodetic.from_gars('348MY16', anchor="nw")
<lon=-006d20m0.000s lat=+053d25m0.000s alt=0.000>
>>> epsg.Geodetic.from_gars('348MY16')
<lon=-006d17m30.000s lat=+053d22m30.000s alt=0.000>
```

**Arguments**:

- `gars` _str_ - gars representation.
- `anchor` _str_ - tile anchor using `n`, `e`, `s` or `w`.

**Returns**:

- `epsglide.Geodetic` - geodetic coordinates.
  
  Global precision of centered GARS coordinates is about `0.0833`
  degrees in longitude ad latitude.

<a id="epsglide.geodesy.Geodetic.geohash"></a>

#### geohash

```python
def geohash(digit: int = 10,
            base: str = "0123456789bcdefghjkmnpqrstuvwxyz") -> str
```

Convert coordinates to geohash. Precision can be set using `digit`
parameter.


```python
>>> london.geohash()
'gcpvj4et8e'
```

**Arguments**:

- `digit` _int_ - digit number of geohash [default: 10].
- `base` _str_ - a 32-sized string of unique caracter. Same base should
  be used to decode correctly the geohash.

**Returns**:

- `str` - geohash representation.

<a id="epsglide.geodesy.Geodetic.from_geohash"></a>

#### from\_geohash

```python
@staticmethod
def from_geohash(geohash: str,
                 base: str = "0123456789bcdefghjkmnpqrstuvwxyz",
                 center: bool = True)
```

Return Geodetic object from geohash.


```python
>>> Geodetic.from_geohash('gcpvj4et8e')
<lon=-000d07m37.19969s lat=+051d31m6.97229s alt=0.0>
```

**Arguments**:

- `base` _str_ - a 32-sized string of unique caracter used to encode the
  geodetic coordinates.

**Returns**:

- `epsglide.Geodetic` - geodetic coordinates.
  
  A `precision` tuple (longitude, latitude) in degrees is added as
  class attribute.
  
```python
>>> epsglide.Geodetic.from_geohash('gcpvj4et8e').precision
(2.682209014892578e-06, 1.341104507446289e-06)
```

<a id="epsglide.geodesy.Geodetic.url_load_location"></a>

#### url\_load\_location

```python
def url_load_location(url, **kwargs)
```

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

**Arguments**:

- `url` _str_ - map provider url containing `%(lon)f` and `%(lat)f`
  format expression to be replaced by longitude and latitude in
  the proper unit according to map provider.
- `**kwargs` _dict_ - key-value pairs to match entries in url according
  to python string formatting.

**Returns**:

  Image data as `bytes` (py3) or `str` (py2).

<a id="epsglide.geodesy.Geodetic.dump_location"></a>

#### dump\_location

```python
def dump_location(name, url, **kwargs)
```

Dump a static map image from map provider into filesystem.

**Arguments**:

- `name` _str_ - a valid filepath.
- `url` _str_ - map provider url containing `%(lon)f` and `%(lat)f`
  format expression to be replaced by longitude and latitude
  found in GPS data.
- `**kwargs` _dict_ - key-value pairs to match entries in url according
  to python string formatting.

