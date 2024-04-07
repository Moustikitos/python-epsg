<a id="epsglide.dataset"></a>

# Module epsglide.dataset

<a id="epsglide.dataset.DATA"></a>

#### epsglide.dataset.DATA

Path where json dataset are stored. On each EPSG dataset request, json data
are stored on this local path to allow introspection when needed and faster
execution.

<a id="epsglide.dataset.DatasetConnexionError"></a>

## DatasetConnexionError Objects

```python
class DatasetConnexionError(Exception)
```

Exception raised when EPSG API is not available.

<a id="epsglide.dataset.DatasetNotFound"></a>

## DatasetNotFound Objects

```python
class DatasetNotFound(Exception)
```

Exception raised when API call status code is not 200.

<a id="epsglide.dataset.DatasetIdentificationError"></a>

## DatasetIdentificationError Objects

```python
class DatasetIdentificationError(Exception)
```

Exception raised when EpsgElement initialized with no info.

<a id="epsglide.dataset.DatumInitializationError"></a>

## DatumInitializationError Objects

```python
class DatumInitializationError(Exception)
```

Exception raised when unmanageable datum parameter occurs.

<a id="epsglide.dataset.EpsgElement"></a>

## EpsgElement Objects

```python
class EpsgElement(object)
```

Represents an EPSG dataset element.

**Attributes**:

- `_struct_` _ctypes.Structure_ - object representing the structure of the
  equivalant C element.
  

**Arguments**:

- `code` _int_ - the EPSG code of the element.
- `name` _str_ - the name of the element.
  

**Raises**:

- `DatasetIdentificationError` - if either EPSG code or name is not
  provided.
- `NotImplementedError` - if searching by keyword is attempted (not
  implemented yet).

<a id="epsglide.dataset.EpsgElement.__repr__"></a>

### EpsgElement.\_\_repr\_\_

```python
def __repr__()
```

Return a string representation of the `EpsgElement` object.

**Returns**:

- `str` - a string representation of the object in the format
  `<ClassName Code: Name>`.

<a id="epsglide.dataset.EpsgElement.populate"></a>

### EpsgElement.populate

```python
def populate()
```

Populate the EPSG dataset element. This method is meant to be
overridden by subclasses.

<a id="epsglide.dataset.Unit"></a>

## Unit Objects

```python
class Unit(EpsgElement)
```

Represents a unit in EPSG dataset.

**Attributes**:

- `ratio` _float_ - The ratio value of the unit.

<a id="epsglide.dataset.Unit.from_target"></a>

### Unit.from\_target

```python
def from_target(value: Union[int, float]) -> float
```

Convert a value to the dataset specific unit.


```python
>>> u = epsglide.dataset.Unit(9003)
>>> u
<Unit 9003: US survey foot>
>>> u.from_target(1) # convert one metre into US survey foot
3.2808333333333333
```

**Arguments**:

- `value` _int|float_ - the value to be converted.
  

**Returns**:

- `float|None` - the converted value, or None if no conversion is
  possible.

<a id="epsglide.dataset.Unit.to_target"></a>

### Unit.to\_target

```python
def to_target(value: Union[int, float]) -> float
```

Convert a value to computation specific units.


```python
>>> u = epsglide.dataset.Unit(9002)
>>> u
<Unit 9002: foot>
>>> u.to_target(1) # convert one international feet into meters
0.3048
```

**Arguments**:

- `value` _int|float_ - the value to be converted.
  

**Returns**:

- `float|None` - the converted value, or None if no conversion is
  possible.

<a id="epsglide.dataset.PrimeMeridian"></a>

## PrimeMeridian Objects

```python
class PrimeMeridian(EpsgElement)
```

Represents a prime meridian in EPSG dataset.

**Attributes**:

- `longitude` _float_ - The longitude value of the prime meridian.

<a id="epsglide.dataset.Ellipsoid"></a>

## Ellipsoid Objects

```python
class Ellipsoid(EpsgElement)
```

Represents an ellipsoid model used in geodetic coordinate reference
systems.

**Methods**:

- `populate` - Populate the `Ellipsoid` object with necessary data,
  including parameters related to its shape and size.

<a id="epsglide.dataset.Ellipsoid.populate"></a>

### Ellipsoid.populate

```python
def populate()
```

Populate the `Ellipsoid` object with necessary data.

This method initializes the internal structure (`_struct_`) of the
`Ellipsoid` object with information about its semi-major axis,
semi-minor axis, flattening, eccentricity, and other related
parameters.

The initialization process depends on whether the ellipsoid's
inverse flattening is provided or calculated from its semi-major
and semi-minor axes.

<a id="epsglide.dataset.GeodeticCoordRefSystem"></a>

## GeodeticCoordRefSystem Objects

```python
class GeodeticCoordRefSystem(EpsgElement)
```

Represents a geodetic coordinate reference system.

**Methods**:

- `populate` - Populate the GeodeticCoordRefSystem object with necessary
  data, including datum and transformation parameters.

<a id="epsglide.dataset.GeodeticCoordRefSystem.populate"></a>

### GeodeticCoordRefSystem.populate

```python
def populate()
```

Populate the `GeodeticCoordRefSystem` object with necessary data.

This method initializes the internal structure (`_struct_`) of the
`GeodeticCoordRefSystem` object with information about the datum,
ellipsoid, prime meridian, and transformation parameters.

**Raises**:

- `DatasetNotFound` - If no transformation is found for the given
  coordinate reference system (CRS) code.
- `DatumInitializationError` - If an unmanageable transformation
  parameter is encountered during initialization.

