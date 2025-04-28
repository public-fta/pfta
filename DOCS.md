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


### Failure models

Three types of failure model may be declared.
The choice of `model_type` determines the other properties that may be set:

1. `Undeveloped`:

   ```
   Mode: <identifier>
   - label: <string>          (optional)
   - comment: <string>        (optional)
   - model_type: Undeveloped
   ```

2. `Fixed`:

   ```
   Mode: <identifier>
   - label: <string>                        (optional)
   - comment: <string>                      (optional)
   - model_type: Fixed
   - probability: <float> | <distribution>  (mandatory)
   - intensity: <float> | <distribution>    (mandatory)
   ```

3. `ConstantRate`:

   ```
   Mode: <identifier>
   - label: <string>                                             (optional)
   - comment: <string>                                           (optional)
   - model_type: ConstantRate
   - failure_rate | mean_failure_time: <float> | <distribution>  (mandatory)
   - repair_rate | mean_repair_time: <float> | <distribution>    (mandatory)
   ```

A declared failure model may be utilised by an event.


## Core objects
