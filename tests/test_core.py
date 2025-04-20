"""
# Public Fault Tree Analyser: test_core.py

Unit testing for `core.py`.

**Copyright 2025 Conway.**
Licensed under the GNU General Public License v3.0 (GPL-3.0-only).
This is free software with NO WARRANTY etc. etc., see LICENSE.
"""

import textwrap
import unittest

from pfta.core import (
    DuplicateIdException, UnsetPropertyException,
    NonPositiveValueException, SubUnitValueException, UnknownInputException,
    FaultTree, Gate,
)


class TestCore(unittest.TestCase):
    def test_fault_tree(self):
        # Duplicate identifier
        self.assertRaises(
            DuplicateIdException,
            FaultTree,
            textwrap.dedent('''
                - time: 1

                Event: EV-001

                Event: EV-001
            '''),
        )

        # Unset time
        self.assertRaises(
            UnsetPropertyException,
            FaultTree,
            '- time_unit: h',
        )

        # Non-positive time
        self.assertRaises(
            NonPositiveValueException,
            FaultTree,
            '- time: 0.',
        )
        self.assertRaises(
            NonPositiveValueException,
            FaultTree,
            '- time: -1',
        )
        self.assertRaises(
            NonPositiveValueException,
            FaultTree,
            '- time: 3, 4, -5',
        )

        # Sub-unit sample size
        self.assertRaises(
            SubUnitValueException,
            FaultTree,
            textwrap.dedent('''
                - time: 1
                - sample_size: 0
            '''),
        )
        self.assertRaises(
            SubUnitValueException,
            FaultTree,
            textwrap.dedent('''
                - time: 1
                - sample_size: -100
            '''),
        )
        self.assertRaises(
            SubUnitValueException,
            FaultTree,
            textwrap.dedent('''
                - time: 1
                - sample_size: 0.9999
            '''),
        )

        # Unknown gate inputs
        self.assertRaises(
            UnknownInputException,
            FaultTree,
            textwrap.dedent('''
                - time: 1

                Gate: GT-001
                - type: AND
                - inputs: EV-YES, EV-NO

                Event: EV-YES
            '''),
        )

    def test_gate(self):
        # Unset type
        self.assertRaises(
            UnsetPropertyException,
            Gate,
            'GT-003', {'label': 'Third gate'},
        )

        # Unset inputs
        self.assertRaises(
            UnsetPropertyException,
            Gate,
            'GT-003', {'label': 'type gate', 'type': 'OR'},
        )

        # Reasonable gate
        try:
            Gate('GT-003', {'type': 'OR', 'input_ids': ['EV-001', 'EV-002']})
        except UnsetPropertyException:
            self.fail('UnsetPropertyException should not have been raised')
