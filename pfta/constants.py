"""
# Public Fault Tree Analyser: constants.py

Shared constants.

**Copyright 2025 Conway.**
Licensed under the GNU General Public License v3.0 (GPL-3.0-only).
This is free software with NO WARRANTY etc. etc., see LICENSE.
"""

import enum
import re

from pfta.common import natural_join_backticks


class LineType(enum.Enum):
    BLANK = 0
    COMMENT = 1
    OBJECT = 2
    PROPERTY = 3


class GateType(enum.Enum):
    OR = 0
    AND = 1


LINE_EXPLAINER = '\n'.join([
    'A line must have one of the following forms:',
    '    <class>: <identifier>  (an object declaration)',
    '    - <key>: <value>       (a property setting)',
    '    # <comment>            (a comment)',
    '    <blank line>           (used before the next declaration)',
])

VALID_CLASSES = ('Event', 'Gate')
CLASS_EXPLAINER = f'An object must have class {natural_join_backticks(VALID_CLASSES, "or")}.'

VALID_ID_REGEX = re.compile(r'[a-z0-9_-]+', flags=re.IGNORECASE)
ID_EXPLAINER = 'An identifier must consist only of ASCII letters, underscores, and hyphens.'

BOOLEAN_FROM_STRING = {
    'True': True,
    'False': False,
}
IS_PAGED_EXPLAINER = (
    f'Boolean property must be {natural_join_backticks(tuple(BOOLEAN_FROM_STRING.keys()), "or")} (case-sensitive).'
)

GATE_TYPE_FROM_STRING = {
    'OR': GateType.OR,
    'AND': GateType.AND,
}
GATE_TYPE_EXPLAINER = (
    f'Gate type must be {natural_join_backticks(tuple(GATE_TYPE_FROM_STRING.keys()), "or")} (case-sensitive).'
)

VALID_KEY_COMBOS_FROM_MODEL_TYPE = {
    'Undeveloped': (
        (),
    ),
    'Fixed': (
        ('probability', 'intensity'),
    ),
    'ConstantRate': (
        ('failure_rate', 'repair_rate'),
        ('failure_rate', 'mean_repair_time'),
        ('mean_failure_time', 'repair_rate'),
        ('mean_failure_time', 'mean_repair_time'),
    ),
}
VALID_MODEL_TYPES = tuple(VALID_KEY_COMBOS_FROM_MODEL_TYPE.keys())
VALID_MODEL_KEYS = tuple(
    key
    for combos in VALID_KEY_COMBOS_FROM_MODEL_TYPE.values()
    for combo in combos
    for key in combo
)
MODEL_TYPE_EXPLAINER = f'Recognised model types are {natural_join_backticks(VALID_MODEL_TYPES)}'

VALID_KEYS_FROM_CLASS = {
    'FaultTree': ('time_unit', 'time', 'seed', 'sample_size'),
    'Event': ('label', 'comment', 'model_type', *VALID_MODEL_KEYS),
    'Gate': ('label', 'is_paged', 'type', 'inputs', 'comment'),
}
KEY_EXPLAINER_FROM_CLASS = {
    'FaultTree': f'Recognised keys are {natural_join_backticks(VALID_KEYS_FROM_CLASS["FaultTree"])}.',
    'Event': f'Recognised keys are {natural_join_backticks(VALID_KEYS_FROM_CLASS["Event"])}.',
    'Gate': f'Recognised keys are {natural_join_backticks(VALID_KEYS_FROM_CLASS["Gate"])}.',
}
