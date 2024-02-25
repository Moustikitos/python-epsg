<a id="epsglide.src"></a>

# epsglide.src

<a id="epsglide.src.Unit"></a>

## Unit Objects

```python
class Unit(ctypes.Structure)
```

Represents a `Unit` structure in C code.

**Attributes**:

- `ratio` _float_ - The ratio value of the unit.

<a id="epsglide.src.Prime"></a>

## Prime Objects

```python
class Prime(ctypes.Structure)
```

Represents a `Prime` structure in C code.

**Attributes**:

- `longitude` _float_ - The longitude value of the prime meridian.

<a id="epsglide.src.Ellipsoid"></a>

## Ellipsoid Objects

```python
class Ellipsoid(ctypes.Structure)
```

Represents an `Ellipsoid` structure in C code.

**Attributes**:

- `a` _float_ - The semi-major axis of the ellipsoid.
- `b` _float_ - The semi-minor axis of the ellipsoid.
- `e` _float_ - The eccentricity of the ellipsoid.
- `f` _float_ - The flattening of the ellipsoid.

<a id="epsglide.src.Datum"></a>

## Datum Objects

```python
class Datum(ctypes.Structure)
```

Represents a `Datum` structure in C code.

**Attributes**:

- `ellipsoid` _Ellipsoid_ - The ellipsoid associated with the datum.
- `prime` _Prime_ - The prime meridian associated with the datum.
- `ds` _float_ - The scale difference parameter.
- `dx` _float_ - The X translation parameter.
- `dy` _float_ - The Y translation parameter.
- `dz` _float_ - The Z translation parameter.
- `rx` _float_ - The X rotation parameter.
- `ry` _float_ - The Y rotation parameter.
- `rz` _float_ - The Z rotation parameter.

<a id="epsglide.src.Crs"></a>

## Crs Objects

```python
class Crs(ctypes.Structure)
```

Represents a `Crs` structure in C code.

**Attributes**:

- `datum` _Datum_ - The datum associated with the coordinate reference
  system.
- `lambda0` _float_ - The longitude of the point from which the values of
  both the geographical coordinates on the ellipsoid and the grid
  coordinates on the projection are deemed to increment or decrement
  for computational purposes. Alternatively it may be considered as
  the longitude of the point which in the absence of application of
  false coordinates has grid coordinates of (0,0). Sometimes known
  as "central meridian" (CM).
- `phi0` _float_ - The latitude of the point from which the values of both
  the geographical coordinates on the ellipsoid and the grid
  coordinates on the projection are deemed to increment or decrement
  for computational purposes. Alternatively it may be considered as
  the latitude of the point which in the absence of application of
  false coordinates has grid coordinates of (0,0).
- `phi1` _float_ - for a conic projection with two standard parallels, this
  is the latitude of one of the parallels of intersection of the cone
  with the ellipsoid. It is normally but not necessarily that nearest
  to the pole. Scale is true along this parallel.
- `phi2` _float_ - for a conic projection with two standard parallels, this
  is the latitude of one of the parallels at which the cone
  intersects with the ellipsoid. It is normally but not necessarily
  that nearest to the equator. Scale is true along this parallel.
- `k0` _float_ - the factor by which the map grid is reduced or enlarged
  during the projection process, defined by its value at the natural
  origin.
- `x0` _float_ - since the natural origin may be at or near the centre of
  the projection and under normal coordinate circumstances would thus
  give rise to negative coordinates over parts of the mapped area,
  this origin is usually given false coordinates which are large
  enough to avoid this inconvenience. The False Easting, FE, is the
  value assigned to the abscissa (east or west) axis of the
  projection grid at the natural origin.
- `y0` _float_ - since the natural origin may be at or near the centre of
  the projection and under normal coordinate circumstances would thus
  give rise to negative coordinates over parts of the mapped area,
  this origin is usually given false coordinates which are large
  enough to avoid this inconvenience. The False Northing, FN, is the
  value assigned to the ordinate (north or south) axis of the
  projection grid at the natural origin.
- `azimut` _float_ - the azimuthal direction (north zero, east of north
  being positive) of the great circle which is the centre line of an
  oblique projection. The azimuth is given at the projection centre.

