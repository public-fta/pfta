# PFTA documentation

## Fault tree text format

Fault tree text is to consist of paragraphs declaring [fault tree properties](#fault-tree-properties-paragraph),
[failure models](#failure-model-paragraph), [events](#event-paragraph), or [gates](#gate-paragraph).

### Fault tree properties paragraph

The fault tree properties paragraph must be the first paragraph.

```
- times: <comma separated floats>  (mandatory; use `nan` for arbitrary time)
- time_unit: <string>              (optional; displayed on intensities and rates in graphical output)
- seed: <string>                   (optional; used when sampling distributions)
- sample_size: <integer>           (optional; default `1`)
- tolerance: <float>               (optional; default `0`; tolerance for truncating probability/intensity computations)
```


### Failure model paragraph

The choice of `model_type` for a failure model determines the parameters that may be set.
Parameter values may be supplied as either:

- A `<float>`, denoting a point estimate (or degenerate distribution); or

- A `<distribution>`, being one of the following:

  - `lognormal(mu=<value>, sigma=<value>)`
  - `loguniform(lower=<value>, upper=<value>)`
  - `normal(mu=<value>, sigma=<value>)`
  - `triangular(lower=<value>, upper=<value>, mode=<value>)`
  - `uniform(lower=<value>, upper=<value>)`


#### Undeveloped

```
Model: <identifier>
- label: <string>          (optional)
- comment: <string>        (optional)
- model_type: Undeveloped
```

Events using an undeveloped model have their failure quantities computed as

```
q(t) = 0,
ω(t) = 0.
```

#### Fixed

```
Model: <identifier>
- label: <string>                        (optional)
- comment: <string>                      (optional)
- model_type: Fixed
- probability: <float> | <distribution>  (mandatory)
- intensity: <float> | <distribution>    (mandatory)
```

Events using a fixed model have their failure quantities computed as

```
q(t) = q₀,
ω(t) = ω₀,
```

where `q₀ = probability` and `ω₀ = intensity`.

#### ConstantRate

```
Model: <identifier>
- label: <string>                                             (optional)
- comment: <string>                                           (optional)
- model_type: ConstantRate
- failure_rate | mean_failure_time: <float> | <distribution>  (mandatory)
- repair_rate | mean_repair_time: <float> | <distribution>    (mandatory)
```

Events using a constant-rate model have their failure quantities computed as

```
q(t) = [λ₀/(λ₀+μ₀)] [1−exp(−(λ₀+μ₀)t)],
ω(t) = λ₀(1−q(t)),
```

where `λ₀ = failure_rate = 1/mean_failure_time` and `μ₀ = repair_rate = 1/mean_repair_time`.


### Event paragraph

An event declaration may do one of the following:

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


### Gate paragraph

```
Gate: <identifier>
- label: <string>                        (optional)
- comment: <string>                      (optional)
- is_paged: True | False                 (optional; default `False`; whether the gate should have its own page in graphical output)
- type: AND | OR                         (mandatory)
- inputs: <comma separated identifiers>  (mandatory)
```


## Core objects

Objects from `pfta.core` that are (directly or indirectly) exposed after invoking `FaultTree(fault_tree_text)`:


### FaultTree

| Attribute | Description |
| - | - |
| `times` | Time values. |
| `time_unit` | Time unit. |
| `seed` | Seed used for sampling distributions. |
| `sample_size` | Sample size for sampling distributions. |
| `tolerance` | Tolerance for truncating probability/intensity computations. |
| `models` | List of [failure models]. |
| `events` | List of [events]. |
| `gates` | List of [gates]. |
| `compile_model_table()` | Produce a [table] of [failure models]. |
| `compile_event_table()` | Produce a [table] of [events]. |
| `compile_gate_table()` | Produce a [table] of [gates]. |
| `compile_cut_set_tables()` | Produce a dictionary from gate identifier to [table] of cut sets. |
| `compile_figures()` | Produce a dictionary from gate identifier to [figure]. |


### Model

| Attribute | Description |
| - | - |
| `id_` | Model identifier. |
| `label` | Model label. |
| `comment` | Model comment. |
| `model_type` | Model type. |
| `is_used` | Whether the model is actually utilised by an event in the fault tree. |


### Event

| Attribute | Description |
| - | - |
| `id_` | Event identifier. |
| `index` | Event index (0-based). |
| `label` | Event label. |
| `comment` | Event comment. |
| `model_id` | Identifier of utilised failure model (or `None`). |
| `model_type` | Model type, if not utilising a failure model. |
| `is_used` | Whether the event is actually utilised by a gate in the fault tree. |
| `flattened_indexer` | [Flattened list] indexer. |
| `actual_model_type` | The actual `model_type`, either from the utilised failure model or the event itself. |
| `parameter_samples` | Dictionary from string parameter to [flattened list] of of sampled values. |
| `computed_expression` | Boolean algebraic representation of the event. |
| `computed_probabilities` | [Flattened list] of computed failure probabilities. |
| `computed_intensities` | [Flattened list] of computed failure intensities. |
| `computed_rates` | [Flattened list] of computed failure rates. |
| `computed_expected_probabilities` | List of computed expected values of failure probability (by time). |
| `computed_probability(time_index, sample_index)` | Produce the computed failure probability associated with `time_index` and `sample_index`. |
| `computed_intensity(time_index, sample_index)` | Produce the computed failure intensity associated with `time_index` and `sample_index`. |
| `computed_rate(time_index, sample_index)` | Produce the computed failure rate associated with `time_index` and `sample_index`. |


### Gate

| Attribute | Description |
| - | - |
| `id_` | Gate identifier. |
| `label` | Gate label. |
| `comment` | Gate comment. |
| `is_paged` | Whether the gate has its own page in graphical output. |
| `type_` | Gate type. |
| `input_ids` | Gate input identifiers. |
| `is_top_gate` | Whether the gate is a top gate (i.e. not an input to another gate). |
| `flattened_indexer` | [Flattened list] indexer. |
| `computed_expression` | Boolean algebraic representation of the gate. |
| `computed_probabilities` | [Flattened list] of computed failure probabilities. |
| `computed_intensities` | [Flattened list] of computed failure intensities. |
| `computed_rates` | [Flattened list] of computed failure rates. |
| `computed_probability(time_index, sample_index)` | Produce the computed failure probability associated with `time_index` and `sample_index`. |
| `computed_intensity(time_index, sample_index)` | Produce the computed failure intensity associated with `time_index` and `sample_index`. |
| `computed_rate(time_index, sample_index)` | Produce the computed failure rate associated with `time_index` and `sample_index`. |


### FlattenedIndexer

| Attribute | Description |
| - | - |
| `time_count` | Count of time values (from fault tree properties, i.e. `len(times)`). |
| `sample_size` | Sample size (from fault tree properties). |
| `flattened_size` | Product of `time_count` and `sample_size`. |
| `get_index(time_index, sample_index)` | Produce the flattened index associated with `time_index` and `sample_index`. |
| `get_slice(time_index)` | Produce the flattened index slice associated with `time_index`. |

Flattened lists of results are effectively indexed by the following comprehension:

```python
[
    (flattened_index := time_index * sample_size + sample_index)
    for time_index, _ in enumerate(times)
    for sample_index in range(sample_size)
]
```


## Presentational objects

Objects from `pfta.presentation` that are produced by the methods of [`FaultTree`]:


### Figure

| Attribute | Description |
| - | - |
| `top_node` | Top node of the figure. |
| `graphics` | List of graphics of the figure. |
| `svg_content()` | Produce the SVG content of the figure. |
| `write_svg()` | Write figure to an SVG file. |


### Table

| Attribute | Description |
| - | - |
| `headings` | Table headings (i.e. column names). |
| `data` | Table data rows. |
| `write_tsv(file_name)` | Write table to a TSV file. |


[`FaultTree`]: #faulttree
[events]: #event
[failure models]: #model
[figure]: #figure
[gates]: #gate
[flattened list]: #flattenedindexer
[table]: #table
