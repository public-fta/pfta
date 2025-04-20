"""
# Public Fault Tree Analyser: constants.py

Shared constants.

**Copyright 2025 Conway.**
Licensed under the GNU General Public License v3.0 (GPL-3.0-only).
This is free software with NO WARRANTY etc. etc., see LICENSE.
"""

import enum


class LineType(enum.Enum):
    OBJECT = 0
    PROPERTY = 1
    COMMENT = 2
    BLANK = 3


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
CLASS_EXPLAINER = 'An object must have class `Event` or `Gate`.'

BOOLEAN_FROM_STRING = {
    'True': True,
    'False': False,
}
IS_PAGED_EXPLAINER = 'Boolean property must be `True` or `False` (case-sensitive)'

GATE_TYPE_FROM_STRING = {
    'OR': GateType.OR,
    'AND': GateType.AND,
}
GATE_TYPE_EXPLAINER = 'Gate type must be `OR` or `AND` (case-sensitive)'

VALID_KEYS_FROM_CLASS = {
    'FaultTree': ('time_unit', 'time'),
    'Event': ('label', 'probability', 'intensity', 'comment'),
    'Gate': ('label', 'is_paged', 'type', 'inputs', 'comment'),
}
KEY_EXPLAINER_FROM_CLASS = {
    'FaultTree': 'Recognised keys are `time_unit` and `time`.',
    'Event': 'Recognised keys are `label`, `probability`, `intensity`, and `comment`.',
    'Gate': 'Recognised keys are `label`, `is_paged`, `type`, `inputs`, and `comment`.',
}
