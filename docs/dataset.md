<a id="epsglide.dataset"></a>

# epsglide.dataset

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

#### \_\_repr\_\_

```python
def __repr__()
```

Return a string representation of the `EpsgElement` object.

**Returns**:

- `str` - a string representation of the object in the format
  `<ClassName Code: Name>`.

<a id="epsglide.dataset.EpsgElement.populate"></a>

#### populate

```python
def populate()
```

Populate the EPSG dataset element. This method is meant to be
overridden by subclasses.

<a id="epsglide.dataset.EpsgElement.to_target"></a>

#### to\_target

```python
def to_target(value: Union[int, float]) -> float
```

Convert a value to the target unit, if applicable, ie: the
`EpsgElement` must contain a `Unit` class as attribute.

**Arguments**:

- `value` _int|float_ - the value to be converted.
  

**Returns**:

- `float|None` - the converted value, or None if no conversion is
  possible.

<a id="epsglide.dataset.EpsgElement.from_target"></a>

#### from\_target

```python
def from_target(value: Union[int, float]) -> float
```

Convert a value from the target unit, if applicable, ie: the
`EpsgElement` must contain a `Unit` class as attribute.

**Arguments**:

- `value` _int|float_ - the value to be converted.
  

**Returns**:

- `float|None` - the converted value, or None if no conversion is
  possible.

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

#### populate

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

#### populate

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

