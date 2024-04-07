<a id="epsglide"></a>

# Module epsglide

This package aims to perform simple requests to [`EPSG GeoRepository API`](https://apps.epsg.org/api/swagger/ui/index) and provides associated geodesic
computation and map projection.

<a id="epsglide.distance"></a>

## distance

```python
def distance(obj: dataset.Ellipsoid, start: Geodetic,
             stop: Geodetic) -> Vincenty_dist
```

Calculate the distance between two points on the ellipsoid surface.

**Arguments**:

- `obj` _dataset.Ellipsoid_ - The ellipsoid object representing the shape of
  the Earth.
- `start` _Geodetic_ - The starting point.
- `stop` _Geodetic_ - The destination point.
  

**Returns**:

- `Vincenty_dist` - The distance between the two points.

<a id="epsglide.destination"></a>

## destination

```python
def destination(obj: dataset.Ellipsoid, start: Geodetic,
                dist: Vincenty_dist) -> Vincenty_dest
```

Calculate the destination point given start point, initial bearing, and
distance.

**Arguments**:

- `obj` _dataset.Ellipsoid_ - The ellipsoid object representing the shape of
  the Earth.
- `start` _Geodetic_ - The starting point.
- `dist` _Vincenty_dist_ - The distance to travel.
  

**Returns**:

- `Vincenty_dest` - The destination point.

<a id="epsglide.to_crs"></a>

## to\_crs

```python
def to_crs(obj: dataset.GeodeticCoordRefSystem,
           crs: dataset.GeodeticCoordRefSystem, lla: Geodetic) -> Geodetic
```

Convert coordinates from one geodetic coordinate reference system to
another.

**Arguments**:

- `obj` _dataset.GeodeticCoordRefSystem_ - The source coordinate reference
  system.
- `crs` _dataset.GeodeticCoordRefSystem_ - The target coordinate reference
  system.
- `lla` _Geodetic_ - The coordinates to convert.
  

**Returns**:

- `Geodetic` - The converted coordinates.

<a id="epsglide.to_wgs84"></a>

## to\_wgs84

```python
def to_wgs84(obj: dataset.GeodeticCoordRefSystem, lla: Geodetic) -> Geodetic
```

Convert coordinates from a geodetic coordinate reference system to WGS84.

**Arguments**:

- `obj` _dataset.GeodeticCoordRefSystem_ - The source coordinate reference
  system.
- `lla` _Geodetic_ - The coordinates to convert.
  

**Returns**:

- `Geodetic` - The converted coordinates in WGS84.

<a id="epsglide.ProjectedCoordRefSystem"></a>

## ProjectedCoordRefSystem Objects

```python
class ProjectedCoordRefSystem(dataset.EpsgElement)
```

Coordinate reference system object allowing projection of geodetic
coordinates to flat map (geographic coordinates).


```python
>>> import epsglide
>>> osgb36 = epsglide.ProjectedCoordRefSystem(27700)
>>> london = epsglide.Geodetic(-0.127005, 51.518602, 0.)  # use degrees
>>> osgb36(london)
<metre:1.000[X=529939.106 Y=181680.962] alt=0.000>
>>> osgb36.Projection
{'Code': 19916, 'Name': 'British National Grid', 'href': 'https://apps.epsg.org/api/v1/Conversion/19916'}
```

**Attributes**:

- `GeodeticCoordRefSystem` _dataset.GeodeticCoordRefSystem_ - geodetic
  reference system.
- `Conversion` _dataset.Conversion_ - projection method and parameters.
- `CoordOperationMethod` _dataset.CoordOperationMethod_ - projection
  description.
- `CoordSystem` _dataset.CoordSystem_ - 2D coordinate system and units.
- `parameters` _list_ - list of `dataset.CoordOperationParameter`.

<a id="epsglide.ProjectedCoordRefSystem.__call__"></a>

### ProjectedCoordRefSystem.\_\_call\_\_

```python
def __call__(
    element: typing.Union[Geodetic, Geographic]
) -> typing.Union[Geodetic, Geographic]
```



<a id="epsglide.ProjectedCoordRefSystem.transform"></a>

### ProjectedCoordRefSystem.transform

```python
def transform(element: typing.Union[Geodetic, Geographic],
              dest_crs) -> Geographic
```



