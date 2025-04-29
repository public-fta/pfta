# PFTA documentation

## Fault tree text format

### Fault tree properties

Fault tree properties are to be set before any objects are declared.

```
- times: <comma separated floats>  (mandatory; use `nan` for arbitrary time)
- time_unit: <string>              (optional; displayed on intensities and rates in graphical output)
- seed: <string>                   (optional; used when sampling distributions)
- sample_size: <integer>           (optional; default `1`)
- tolerance: <float>               (optional; default `0`; tolerance for truncating probability/intensity computations)
```


### Failure models

Three types of failure model may be declared.
The choice of `model_type` determines the parameter properties that may be set:

1. `Undeveloped`:

   ```
   Model: <identifier>
   - label: <string>          (optional)
   - comment: <string>        (optional)
   - model_type: Undeveloped
   ```

2. `Fixed`:

   ```
   Model: <identifier>
   - label: <string>                        (optional)
   - comment: <string>                      (optional)
   - model_type: Fixed
   - probability: <float> | <distribution>  (mandatory)
   - intensity: <float> | <distribution>    (mandatory)
   ```

3. `ConstantRate`:

   ```
   Model: <identifier>
   - label: <string>                                             (optional)
   - comment: <string>                                           (optional)
   - model_type: ConstantRate
   - failure_rate | mean_failure_time: <float> | <distribution>  (mandatory)
   - repair_rate | mean_repair_time: <float> | <distribution>    (mandatory)
   ```

For the parameter properties, the value may be supplied as either:

- A `<float>`, denoting a point estimate (or degenerate distribution); or
- A `<distribution>`, being one of the following:
  - `lognormal(mu=<value>, sigma=<value>)`
  - `loguniform(lower=<value>, upper=<value>)`
  - `normal(mu=<value>, sigma=<value>)`
  - `triangular(lower=<value>, upper=<value>, mode=<value>)`
  - `uniform(lower=<value>, upper=<value>)`

A declared failure model may be utilised by an event.


### Events

An event declaration may either:

1. Utilise a declared failure model:

   ```
   Event: <identifier>
   - label: <string>      (optional)
   - comment: <string>    (optional)
   - model: <identifier>
   ```

2. Utilise its own failure model properties:

   ```
   Event: <identifier>
   - label: <string>                                 (optional)
   - comment: <string>                               (optional)
   - model_type: Undeveloped | Fixed | ConstantRate
   # <followed by the parameter properties relevant to the chosen `model_type`>
   ```


### Gates

Gate declarations are straightforward:

```
Gate: <identifier>
- label: <string>                        (optional)
- comment: <string>                      (optional)
- is_paged: True | False                 (optional; default `False`; whether the gate should have its own page in graphical output)
- type: AND | OR                         (mandatory)
- inputs: <comma separated identifiers>  (mandatory)
```


## Core objects

Objects from `pfta.core` that are (directly or indirectly) exposed after instantiating a `FaultTree(fault_tree_text)`:


### `FaultTree`

| Attribute | Description |
| - | - |
| `times` | Time values. |
| `time_unit` | Time unit. |
| `seed` | Seed used for sampling distributions. |
| `sample_size` | Sample size for sampling distributions. |
| `tolerance` | Tolerance for truncating probability/intensity computations. |
| `models` | List of [failure models](#model). |
| `events` | List of [events](#event). |
| `gates` | List of [gates](#gate). |


### `Model`

| Attribute | Description |
| - | - |
| `id_` | Model identifier. |
| `label` | Model label. |
| `comment` | Model comment. |
| `model_type` | Model type. |
| `is_used` | Whether the model is actually utilised by an event in the fault tree. |


### `Event`

| Attribute | Description |
| - | - |
| `id_` | Event identifier. |
| `index` | Event index (0-based). |
| `label` | Event label. |
| `comment` | Event comment. |
| `model_id` | Identifier of utilised failure model (or `None`). |
| `model_type` | Model type, if not utilising a failure model. |
| `is_used` | Whether the event is actually utilised by a gate in the fault tree. |
| `actual_model_type` | The actual `model_type`, either from the utilised failure model or the event itself. |
| `parameter_samples` | Dictionary from string parameter to [flattened list] of of sampled values. |
| `computed_expression` | Boolean algebraic representation of the event. |
| `computed_probabilities` | [Flattened list] of computed failure probabilities. |
| `computed_intensities` | [Flattened list] of computed failure intensities. |
| `computed_rates` | [Flattened list] of computed failure rates. |


### `Gate`

| Attribute | Description |
| - | - |
| `id_` | Gate identifier. |
| `label` | Gate label. |
| `comment` | Gate comment. |
| `is_paged` | Whether the gate has its own page in graphical output. |
| `type_` | Gate type. |
| `input_ids` | Gate input identifiers. |
| `is_top_gate` | Whether the gate is a top gate (i.e. not an input to another gate). |
| `computed_expression` | Boolean algebraic representation of the gate. |
| `computed_probabilities` | [Flattened list] of computed failure probabilities. |
| `computed_intensities` | [Flattened list] of computed failure intensities. |
| `computed_rates` | [Flattened list] of computed failure rates. |


## Flattened lists

Flattened lists of results are of length `len(times) * sample_size` (from the fault tree properties),
and effectively indexed by the following comprehension:

```python
[
    (flattened_index := time_index * sample_size + sample_index)
    for time_index, _ in enumerate(times)
    for sample_index in range(sample_size)
]
```


[flattened list]: #flattened-lists
