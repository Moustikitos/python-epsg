<a id="epsglide"></a>

# epsglide

This package aims to perform simple requests to [`EPSG GeoRepository API`](https://apps.epsg.org/api/swagger/ui/index) and provides associated geodesic
computation and map projection.

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

#### \_\_call\_\_

```python
def __call__(
    element: typing.Union[Geodetic, Geographic]
) -> typing.Union[Geodetic, Geographic]
```



<a id="epsglide.ProjectedCoordRefSystem.transform"></a>

#### transform

```python
def transform(element: typing.Union[Geodetic, Geographic],
              dest_crs) -> Geographic
```



