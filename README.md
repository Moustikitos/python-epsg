# Python `epsg` package

This package aims to perform simple requests to [`EPSG Registry API`](https://apps.epsg.org/api/swagger/ui/index) and provides associated geodesic computation and map projection.

## EPSG dataset requests

```python
>>> import epsg
>>> wgs84 = epsg.dataset.Ellipsoid(7030)
>>> wgs84.Name
<Ellipsoid #7030: WGS 84>
>>> crs = epsg.ProjectedCoordRefSystem(26730)
>>> crs
<ProjectedCoordRefSystem #26730: NAD27 / Alabama West>
```

## Great circle computation

```python
>>> dublin = epsg.Geodesic(-6.272877, 53.344606, 105.)
>>> london = epsg.Geodesic(-0.127005, 51.518602, 0.)
>>> dist = epsg.geoid.distance(wgs84, dublin, london)
>>> dist
<Dist 464.572km initial bearing=113.5° final bearing=118.3°>
>>> epsg.geoid.destination(wgs84, dublin, dist)
<Dest lon=-000°07'37.21798" lat=+051°31'6.96719" end bearing=118.3°>
>>> london
<lon=-000°07'37.21800" lat=+051°31'6.96720" alt=0.0>
```

## Datum convertions
