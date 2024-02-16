# Python `epsglide` package

This package aims to perform simple requests to [`EPSG Registry API`](https://apps.epsg.org/api/swagger/ui/index) and provides associated geodesic computation and map projection.

## EPSG dataset requests and projection

```python
>>> import math, epsglide
>>> crs = epsglide.ProjectedCoordRefSystem(26730)
>>> crs
<ProjectedCoordRefSystem #26730: NAD27 / Alabama West>
>>> point = epsglide.Geodesic(math.degrees(crs.lambda0), math.degrees(crs.phi0))
>>> crs(point)
<US survey foot:3.281[X=152400.305 Y=0.000] alt=0.000>
>>> crs(crs(point))
<lon=-087°18'0.00000" lat=+030°00'0.00000" alt=0.0>
```

## Great circle computation

```python
>>> wgs84 = epsglide.dataset.Ellipsoid(7030)
>>> dublin = epsglide.Geodesic(-6.272877, 53.344606, 105.)
>>> london = epsglide.Geodesic(-0.127005, 51.518602, 0.)
>>> dist = wgs84.distance(dublin, london) 
>>> dist
<464.572km initial bearing=113.5° final bearing118.3°>
>>> wgs84.destination(dublin, dist) 
<lon=-000°07'37.21798" lat=+051°31'6.96719" end bearing=118.3°>
>>> london
<lon=-000°07'37.21800" lat=+051°31'6.96720" alt=0.0>
```
