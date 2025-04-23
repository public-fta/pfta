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
    DuplicateIdException, UnsetPropertyException, InvalidModelKeyComboException,
    NegativeValueException, SubUnitValueException, UnknownInputException, CircularInputsException,
    FaultTree, Event, Gate,
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
                - model_type: Undeveloped

                Event: EV-001
                - model_type: Undeveloped
            '''),
        )

        # Unset time
        self.assertRaises(
            UnsetPropertyException,
            FaultTree,
            '- time_unit: h',
        )

        # Negative time
        try:
            FaultTree('- time: 0, nan')
        except NegativeValueException:
            self.fail('NegativeValueException should not have been raised')

        self.assertRaises(
            NegativeValueException,
            FaultTree,
            '- time: -1',
        )
        self.assertRaises(
            NegativeValueException,
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
                - model_type: Undeveloped
            '''),
        )

        # Circular gate inputs
        self.assertRaises(
            CircularInputsException,
            FaultTree,
            textwrap.dedent('''
                - time: 1

                Gate: A
                - type: AND
                - inputs: A
            '''),
        )
        self.assertRaises(
            CircularInputsException,
            FaultTree,
            textwrap.dedent('''
                - time: 1

                Gate: Paper
                - type: OR
                - inputs: Scissors, Lizard

                Gate: Scissors
                - type: OR
                - inputs: Spock, Rock

                Gate: Spock
                - type: OR
                - inputs: Lizard, Paper

                Gate: Lizard
                - type: OR
                - inputs: Rock, Scissors

                Gate: Rock
                - type: OR
                - inputs: Paper, Spock
            '''),
        )

    def test_event(self):
        # Reasonable event
        try:
            Event('EV-001', 0, {'label': 'First event', 'model_type': 'Undeveloped'})
        except (UnsetPropertyException, InvalidModelKeyComboException):
            self.fail('UnsetPropertyException or InvalidModelKeyComboException should not have been raised')

        # Unset model type
        self.assertRaises(
            UnsetPropertyException,
            Event,
            'EV-001', 0, {'label': 'First event'},
        )

        # Reasonable model key combo
        try:
            Event(
                'EV-001',
                0,
                {'label': 'First event', 'model_type': 'ConstantRate', 'mean_failure_time': '100', 'repair_rate': '10'},
            )
        except InvalidModelKeyComboException:
            self.fail('InvalidModelKeyComboException should not have been raised')

        # Invalid model key combo
        self.assertRaises(
            InvalidModelKeyComboException,
            Event,
            'EV-001',
            0,
            {'label': 'First event', 'model_type': 'ConstantRate', 'mean_failure_time': '100', 'failure_rate': '10'},
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
