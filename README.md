# Python `epsglide` package

This package aims to perform simple requests to [`EPSG GeoRepository API`](https://apps.epsg.org/api/swagger/ui/index) and provides associated geodesic computation and map projection.

## EPSG dataset requests and projection

```python
>>> import math, epsglide
>>> crs = epsglide.ProjectedCoordRefSystem(26730)
>>> crs
<ProjectedCoordRefSystem 26730: NAD27 / Alabama West>
>>> point = epsglide.Geodesic(math.degrees(crs.lambda0), math.degrees(crs.phi0))
>>> crs(point)
<US survey foot:3.281[X=152400.305 Y=0.000] alt=0.000>
>>> crs(crs(point))
<lon=-087d18m0.00000s lat=+030d00m0.00000s alt=0.0>
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
<lon=-000d07m37.21798s lat=+051d31m6.96719s end bearing=118.3°>
>>> london
<lon=-000d07m37.21800s lat=+051d31m6.96720s alt=0.0>
```

## Support this project

[![Liberapay receiving](https://img.shields.io/liberapay/goal/Toons?logo=liberapay)](https://liberapay.com/Toons/donate)
[![Paypal me](https://img.shields.io/badge/PayPal-toons-00457C?logo=paypal&logoColor=white)](https://paypal.me/toons)
[![Bitcoin](https://img.shields.io/badge/Donate-bc1q6aqr0hfq6shwlaux8a7ydvncw53lk2zynp277x-ff9900?logo=bitcoin)](/docs/img/bc1q6aqr0hfq6shwlaux8a7ydvncw53lk2zynp277x.png)
