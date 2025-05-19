# PFTA documentation

This documentation describes the [fault tree text syntax], the [core objects], and the [presentational objects]
of PFTA.

See the main readme for [installation], [command line usage], and a [scripting example].


## Fault tree text syntax

Fault tree text is to consist of paragraphs declaring [fault tree properties](#fault-tree-properties-paragraph),
[failure models](#failure-model-paragraph), [events](#event-paragraph), or [gates](#gate-paragraph).

### Fault tree properties paragraph

The fault tree properties paragraph must be the first paragraph.

```
- times: <comma separated floats>   (mandatory; use `nan` for arbitrary time)
- time_unit: <string>               (optional; displayed on intensities and rates in graphical output)
- seed: <string>                    (optional; used when sampling distributions)
- sample_size: <integer>            (optional; default `1`)
- computational_tolerance: <float>  (optional; default `0`; tolerance for truncating probability/intensity computations)
- significant_figures: <integer>    (optional; default `3`; number of significant figures displayed in SVG output)
- scientific_exponent: <integer>    (optional; default `3`; exponent threshold for scientific notation in SVG output)
```


### Failure model paragraph

The choice of `model_type` for a failure model determines the parameters that may be set.
Parameter values may be supplied as either:

- A `<float>`, denoting a point estimate (or degenerate distribution); or

- A `<distribution>`, being one of the following:

  - `beta(alpha=<value>, beta=<value>)`
  - `gamma(alpha=<value>, lambda=<value>)`
  - `lognormal(mu=<value>, sigma=<value>)`
  - `loguniform(lower=<value>, upper=<value>)`
  - `normal(mu=<value>, sigma=<value>)`
  - `triangular(lower=<value>, upper=<value>, mode=<value>)`
  - `uniform(lower=<value>, upper=<value>)`


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

#### True | False

```
Model: <identifier>
- label: <string>           (optional)
- comment: <string>         (optional)
- model_type: True | False
```

Events using a Boolean model are eternally unchanging.
Cut sets are simplified using the Boolean value (`True` or `False`).


### Event paragraph

An event declaration may do one of the following:

1. Utilise a declared failure model:

   ```
   Event: <identifier>
   - label: <string>                          (optional)
   - comment: <string>                        (optional)
   - model: <identifier>
   - appearance: Basic | Undeveloped | House  (optional; default `Basic`)
   ```

2. Utilise its own failure model properties:

   ```
   Event: <identifier>
   - label: <string>                                  (optional)
   - comment: <string>                                (optional)
   - model_type: Fixed | ConstantRate | True | False
   # (followed by the parameter properties relevant to the chosen `model_type`)
   - appearance: Basic | Undeveloped | House          (optional; default `Basic`)
   ```


### Gate paragraph

```
Gate: <identifier>
- label: <string>                          (optional)
- comment: <string>                        (optional)
- is_paged: True | False                   (optional; default `False`; whether the gate should have its own page in graphical output)
- type: NULL | AND | OR | VOTE(<integer>)  (mandatory)
- inputs: <comma separated identifiers>    (mandatory)
```


## Core objects

Objects from `pfta.core` that are (directly or indirectly) exposed after invoking `FaultTree(fault_tree_text)`:


### FaultTree

| Attribute | Description |
| - | - |
| `times` | List of time values. |
| `time_unit` | Time unit. |
| `seed` | Seed used for sampling distributions. |
| `sample_size` | Sample size for sampling distributions. |
| `computational_tolerance` | Tolerance for truncating probability/intensity computations. |
| `significant_figures` | Number of significant figures displayed in SVG output. |
| `scientific_exponent` | Exponent threshold for scientific notation in SVG output. |
| `models` | List of [failure models]. |
| `events` | List of [events]. |
| `gates` | List of [gates]. |
| `compile_model_table()` | Produce a [table] of [failure models]. |
| `compile_event_table()` | Produce a [table] of [events]. |
| `compile_gate_table()` | Produce a [table] of [gates]. |
| `compile_cut_set_tables()` | Produce a dictionary from gate identifier to [table] of cut sets. |
| `compile_importance_tables()` | Produce a dictionary from gate identifier to [table] of event importances. |
| `compile_figures()` | Produce a nested dictionary from time to gate identifier to [figure]. |


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
| `parameter_samples` | Dictionary from string parameter to [flattened list] of sampled values. |
| `computed_expression` | Boolean algebraic representation of the event. |
| `computed_probabilities` | [Flattened list] of computed failure probabilities. |
| `computed_intensities` | [Flattened list] of computed failure intensities. |
| `computed_rates` | [Flattened list] of computed failure rates. |
| `computed_expected_probabilities` | List of computed expected values of failure probability (by time). |
| `computed_expected_intensities` | List of computed expected values of failure intensity (by time). |
| `computed_expected_rates` | List of computed expected values of failure rate (by time). |
| `get_computed_probability(time_index, sample_index)` | Produce the computed failure probability associated with `time_index` and `sample_index`. |
| `get_computed_intensity(time_index, sample_index)` | Produce the computed failure intensity associated with `time_index` and `sample_index`. |
| `get_computed_rate(time_index, sample_index)` | Produce the computed failure rate associated with `time_index` and `sample_index`. |


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
| `computed_expected_probabilities` | List of computed expected values of failure probability (by time). |
| `computed_expected_intensities` | List of computed expected values of failure intensity (by time). |
| `computed_expected_rates` | List of computed expected values of failure rate (by time). |
| `get_computed_probability(time_index, sample_index)` | Produce the computed failure probability associated with `time_index` and `sample_index`. |
| `get_computed_intensity(time_index, sample_index)` | Produce the computed failure intensity associated with `time_index` and `sample_index`. |
| `get_computed_rate(time_index, sample_index)` | Produce the computed failure rate associated with `time_index` and `sample_index`. |


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
    for time_index in range(len(times))
    for sample_index in range(sample_size)
]
```


## Presentational objects

Objects from `pfta.presentation` that are produced by the methods of [`FaultTree`]:


### Figure

| Attribute | Description |
| - | - |
| `id_` | Identifier of the top node of the figure. |
| `label` | Label of the top node of the figure. |
| `top_node` | Top node of the figure. |
| `graphics` | List of graphics of the figure. |
| `svg_content()` | Produce the SVG content of the figure. |
| `write_svg(file_name)` | Write the figure to an SVG file. |


### Index

| Attribute | Description |
| - | - |
| `times` | List of time values. |
| `time_unit` | Time unit. |
| `figures_from_object` | Dictionary from event/gate to set of figures. |
| `objects_from_figure` | Dictionary from figure to set of events/gates. |
| `html_content()` | Produce the HTML content of the figure index. |
| `write_html(file_name)` | Write the figure index to an HTML file. |


### Table

| Attribute | Description |
| - | - |
| `headings` | Table headings (i.e. column names). |
| `data` | Table data rows. |
| `write_tsv(file_name)` | Write table to a TSV file. |


[fault tree text syntax]: #fault-tree-text-syntax
[core objects]: #core-objects
[presentational objects]: #presentational-objects
[installation]: README.md#installation
[command line usage]: README.md#usage-command-line
[scripting example]: README.md#usage-scripting-example

[`FaultTree`]: #faulttree
[events]: #event
[failure models]: #model
[figure]: #figure
[gates]: #gate
[flattened list]: #flattenedindexer
[table]: #table
