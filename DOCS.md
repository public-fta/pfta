# PFTA documentation

## Fault tree text format

### Fault tree properties

Fault tree properties are to be set before any objects are declared.

```
- time: <comma separated floats>  (mandatory; use `nan` for arbitrary time)
- time_unit: <string>             (optional; displayed on intensities and rates in graphical output)
- seed: <string>                  (optional; used when sampling distributions)
- sample_size: <integer>          (optional; default `1`)
- tolerance: <float>              (optional; default `0`; tolerance for truncating probability/intensity computations)
```


## Core objects
