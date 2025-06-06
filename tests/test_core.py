"""
# Public Fault Tree Analyser: test_core.py

Unit testing for `core.py`.

**Copyright 2025 Conway.**
Licensed under the GNU General Public License v3.0 (GPL-3.0-only).
This is free software with NO WARRANTY etc. etc., see LICENSE.
"""

import textwrap
import unittest

from pfta.constants import ModelType, GateType
from pfta.core import (
    DuplicateIdException, UnsetPropertyException, ModelPropertyClashException, InvalidModelKeyComboException,
    NegativeValueException, SubUnitValueException, InvalidComputationalToleranceException,
    UnknownModelException, UnknownInputException, InputCountException, CircularInputsException,
    DistributionSamplingError, InvalidProbabilityValueException,
    FaultTree, Model, Event, Gate,
)
from pfta.sampling import DegenerateDistribution, LogNormalDistribution, UniformDistribution


class TestCore(unittest.TestCase):
    def test_fault_tree(self):
        # Duplicate identifier
        self.assertRaises(
            DuplicateIdException,
            FaultTree,
            textwrap.dedent('''
                - times: 1

                Event: EV-001
                - model_type: Fixed
                - probability: 1
                - intensity: 0

                Event: EV-001
                - model_type: Fixed
                - probability: 1
                - intensity: 0
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
            FaultTree('- times: 0, nan')
        except NegativeValueException:
            self.fail('NegativeValueException should not have been raised')

        self.assertRaises(
            NegativeValueException,
            FaultTree,
            '- times: -1',
        )
        self.assertRaises(
            NegativeValueException,
            FaultTree,
            '- times: 3, 4, -5',
        )

        # Sub-unit sample size
        self.assertRaises(
            SubUnitValueException,
            FaultTree,
            textwrap.dedent('''
                - times: 1
                - sample_size: 0
            '''),
        )
        self.assertRaises(
            SubUnitValueException,
            FaultTree,
            textwrap.dedent('''
                - times: 1
                - sample_size: -100
            '''),
        )

        # Bad computational tolerance
        self.assertRaises(
            InvalidComputationalToleranceException,
            FaultTree,
            textwrap.dedent('''
                - times: 1
                - computational_tolerance: -1
            '''),
        )
        self.assertRaises(
            InvalidComputationalToleranceException,
            FaultTree,
            textwrap.dedent('''
                - times: 1
                - computational_tolerance: -1e-16
            '''),
        )
        self.assertRaises(
            InvalidComputationalToleranceException,
            FaultTree,
            textwrap.dedent('''
                - times: 1
                - computational_tolerance: 1
            '''),
        )
        self.assertRaises(
            InvalidComputationalToleranceException,
            FaultTree,
            textwrap.dedent('''
                - times: 1
                - computational_tolerance: 1.0000000000000001
            '''),
        )
        self.assertRaises(
            InvalidComputationalToleranceException,
            FaultTree,
            textwrap.dedent('''
                - times: 1
                - computational_tolerance: 2
            '''),
        )
        self.assertRaises(
            InvalidComputationalToleranceException,
            FaultTree,
            textwrap.dedent('''
                - times: 1
                - computational_tolerance: nan
            '''),
        )
        self.assertRaises(
            InvalidComputationalToleranceException,
            FaultTree,
            textwrap.dedent('''
                - times: 1
                - computational_tolerance: inf
            '''),
        )

        # Unknown models
        self.assertRaises(
            UnknownModelException,
            FaultTree,
            textwrap.dedent('''
                - times: 1

                Event: EV-001
                - model: MD-NO

                Model: MD-YES
                - model_type: Fixed
                - probability: 1
                - intensity: 0
            '''),
        )

        # Unknown gate inputs
        self.assertRaises(
            UnknownInputException,
            FaultTree,
            textwrap.dedent('''
                - times: 1

                Gate: GT-001
                - type: AND
                - inputs: EV-YES, EV-NO

                Event: EV-YES
                - model_type: Fixed
                - probability: 1
                - intensity: 0
            '''),
        )

        # Incorrect input count on NULL gate
        self.assertRaises(
            InputCountException,
            FaultTree,
            textwrap.dedent('''
                - times: 1

                Gate: GT-001
                - type: NULL
                - inputs: ,

                Event: EV-YES
                - model_type: True
            '''),
        )
        self.assertRaises(
            InputCountException,
            FaultTree,
            textwrap.dedent('''
                - times: 1

                Gate: GT-001
                - type: NULL
                - inputs: EV-YES, EV-NO

                Event: EV-YES
                - model_type: True

                Event: EV-NO
                - model_type: False
            '''),
        )

        # Circular gate inputs
        self.assertRaises(
            CircularInputsException,
            FaultTree,
            textwrap.dedent('''
                - times: 1

                Gate: A
                - type: AND
                - inputs: A
            '''),
        )
        self.assertRaises(
            CircularInputsException,
            FaultTree,
            textwrap.dedent('''
                - times: 1

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

    def test_model(self):
        # Unset model type
        self.assertRaises(
            UnsetPropertyException,
            Model,
            'MD-001', {'label': 'First model'},
        )

        # Reasonable model key combo
        try:
            Model(
                'MD-001',
                {
                    'label': 'First model',
                    'model_type': ModelType.CONSTANT_RATE,
                    'mean_failure_time': DegenerateDistribution(value=100, line_number=9),
                    'repair_rate': DegenerateDistribution(value=10, line_number=10),
                },
            )
        except InvalidModelKeyComboException:
            self.fail('InvalidModelKeyComboException should not have been raised')

        # Invalid model key combo
        self.assertRaises(
            InvalidModelKeyComboException,
            Model,
            'MD-001',
            {
                'label': 'First model',
                'model_type': ModelType.CONSTANT_RATE,
                'mean_failure_time': DegenerateDistribution(value=100, line_number=9),
                'failure_rate': DegenerateDistribution(value=10, line_number=10),
            },
        )

        # Overflow when sampling a distribution
        self.assertRaises(
            DistributionSamplingError,
            Model.generate_parameter_samples,
            {'failure_rate': LogNormalDistribution(mu=1, sigma=1e6, line_number=6)}, 100,
        )

        # Invalid probability
        self.assertRaises(
            InvalidProbabilityValueException,
            Model.generate_parameter_samples,
            {'probability': UniformDistribution(lower=3, upper=4, line_number=6)}, 100,
        )

        # Negative failure rate
        self.assertRaises(
            NegativeValueException,
            Model.generate_parameter_samples,
            {'failure_rate': UniformDistribution(lower=-4, upper=-3, line_number=6)}, 100,
        )

    def test_event(self):
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
                {
                    'label': 'First event',
                    'model_type': ModelType.CONSTANT_RATE,
                    'mean_failure_time': DegenerateDistribution(value=100, line_number=9),
                    'repair_rate': DegenerateDistribution(value=10, line_number=10),
                },
            )
        except InvalidModelKeyComboException:
            self.fail('InvalidModelKeyComboException should not have been raised')

        # Model property clash
        self.assertRaises(
            ModelPropertyClashException,
            Event,
            'EV-001',
            0,
            {'label': 'First event', 'model_type': ModelType.CONSTANT_RATE, 'model_id': 'MD-001'},
        )
        self.assertRaises(
            ModelPropertyClashException,
            Event,
            'EV-001',
            0,
            {
                'label': 'First event',
                'model_id': 'MD-001',
                'mean_failure_time': DegenerateDistribution(value=100, line_number=9),
                'failure_rate': DegenerateDistribution(value=10, line_number=10),
            },
        )

        # Invalid model key combo
        self.assertRaises(
            InvalidModelKeyComboException,
            Event,
            'EV-001',
            0,
            {
                'label': 'First event',
                'model_type': ModelType.CONSTANT_RATE,
                'mean_failure_time': DegenerateDistribution(value=100, line_number=9),
                'failure_rate': DegenerateDistribution(value=10, line_number=10),
            },
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
            'GT-003', {'label': 'type gate', 'type': GateType.OR},
        )

        # Reasonable gate
        try:
            Gate('GT-003', {'type': GateType.OR, 'input_ids': ['EV-001', 'EV-002']})
        except UnsetPropertyException:
            self.fail('UnsetPropertyException should not have been raised')
