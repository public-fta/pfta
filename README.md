# Public Fault Tree Analyser (PFTA)

Free and open-source fault tree analysis.

- For rudimentary documentation, see [`DOCS.md`].
- For an overview of the mathematics, see [`MATHS.md`].


## Features

- Enforces declaration of at least one value of time `t`.
- Supports the general fault tree analysis framework where objects can have
  *both* a failure probability `q(t)` and a failure intensity `ω(t)` (with failure rate `λ(t) = ω(t) / (1 − q(t))`).
- Supports Monte Carlo for failure parameters (sampling of distributions) out of the box.


## Limitations

- Does not support negative logic (NOT gates). Only supports coherent fault trees (AND gates, OR gates).
- Does not support common cause failure groups.


## Textual input

PFTA reads a textual representation of a fault tree. For example:

```
- times: 1, 2, 3, 5, 10, 100, 1000
- time_unit: h
- seed: candle
- sample_size: 1000

Gate: CAN
- label: Candlelight fails
- type: OR
- inputs: IGN, EXT

Gate: IGN
- label: Candle fails to ignite
- type: AND
- inputs: MAT, LTR

Event: MAT
- label: Single match fails to ignite candle
- model_type: Fixed
- probability: triangular(lower=0.1, upper=0.3, mode=0.2)
- intensity: 0

Event: LTR
- label: Lighter fails to ignite candle
- model_type: Fixed
- probability: loguniform(lower=0.001, upper=0.01)
- intensity: 0

Event: EXT
- label: Candle extinguishes
- model_type: ConstantRate
- mean_failure_time: 3
- mean_repair_time: inf
```

This allows for text-based version control of a fault tree.


## Output

Output files consist of:

- a table (TSV) of events,
- a table (TSV) of gates,
- a table (TSV) of cut sets under each gate, and
- vector graphics (SVG) for each top gate and paged gate (**TODO**).


## Installation

```
$ pip3 install pfta
```

- If simply using as a command line tool, do `pipx` instead of `pip3` to avoid having to set up a virtual environment.
- If using Windows, do `pip` instead of `pip3`.


## Usage (command line)

```
$ pfta [-h] [-v] ft.txt

Perform a fault tree analysis.

positional arguments:
  ft.txt         fault tree text file; output is written to `{ft.txt}.out/`

options:
  -h, --help     show this help message and exit
  -v, --version  show program's version number and exit
```


## Usage (scripting example)

```python
from pfta.core import FaultTree

fault_tree = FaultTree('''
- times: nan

Event: A
- model_type: Fixed
- probability: 0
- intensity: 0.9

Event: B
- model_type: Fixed
- probability: 0.7
- intensity: 0

Event: C
- model_type: Fixed
- probability: 0
- intensity: 1e-4

Gate: AB
- type: AND
- inputs: A, B

Gate: AB_OR_C
- type: OR
- inputs: AB, C
''')

fault_tree.gates[0]
# Gate(id_='AB', label=None, is_paged=False, type_=<GateType.AND: 1>, input_ids=['A', 'B'], input_ids_line_number=21, comment=None, is_top_gate=False, computed_expression=Expression(Term(0b11)), computed_probabilities=[0.0], computed_intensities=[0.63], computed_rates=[0.63])

fault_tree.gates[0].computed_rates
# [0.63]

fault_tree.gates[1]
# Gate(id_='AB_OR_C', label=None, is_paged=False, type_=<GateType.OR: 0>, input_ids=['AB', 'C'], input_ids_line_number=25, comment=None, is_top_gate=True, computed_expression=Expression(Term(0b11), Term(0b100)), computed_probabilities=[0.0], computed_intensities=[0.6301], computed_rates=[0.6301])

fault_tree.gates[1].computed_rates
# [0.6301]
```


## Licence

**Copyright 2025 Conway.** <br>
Licensed under the GNU General Public License v3.0 (GPL-3.0-only). <br>
This is free software with NO WARRANTY etc. etc., see [`LICENSE`].


[`DOCS.md`]: DOCS.md
[`LICENSE`]: LICENSE
[`MATHS.md`]: MATHS.md
