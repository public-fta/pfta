"""
# Public Fault Tree Analyser: core.py

Core fault tree analysis classes.

**Copyright 2025 Conway.**
Licensed under the GNU General Public License v3.0 (GPL-3.0-only).
This is free software with NO WARRANTY etc. etc., see LICENSE.
"""

import random
import statistics
import traceback
from typing import Optional

from pfta.boolean import Term, Expression
from pfta.common import natural_repr, format_cut_set, natural_join_backticks
from pfta.computation import (
    ComputationalCache,
    constant_rate_model_probability, constant_rate_model_intensity,
    disjunction_probability, disjunction_intensity,
)
from pfta.constants import LineType, EventAppearance, GateType, VALID_KEY_COMBOS_FROM_MODEL_TYPE, VALID_MODEL_KEYS
from pfta.parsing import (
    parse_lines, parse_paragraphs, parse_assemblies,
    parse_fault_tree_properties, parse_model_properties, parse_event_properties, parse_gate_properties,
)
from pfta.presentation import Figure, Table
from pfta.sampling import Distribution
from pfta.utilities import robust_divide, robust_invert, find_cycles
from pfta.woe import ImplementationError, FaultTreeTextException


def memoise(attribute_name: str):
    """
    Custom decorator `@memoise` for caching the result of a function into a given attribute (initially None).
    """
    def decorator(function: callable):
        def wrapper(self, *args, **kwargs):
            if getattr(self, attribute_name) is None:
                setattr(self, attribute_name, function(self, *args, **kwargs))

            return getattr(self, attribute_name)

        return wrapper

    return decorator


class DuplicateIdException(FaultTreeTextException):
    pass


class UnsetPropertyException(FaultTreeTextException):
    pass


class ModelPropertyClashException(FaultTreeTextException):
    pass


class InvalidModelKeyComboException(FaultTreeTextException):
    pass


class NegativeValueException(FaultTreeTextException):
    pass


class SubUnitValueException(FaultTreeTextException):
    pass


class InvalidToleranceException(FaultTreeTextException):
    pass


class UnknownModelException(FaultTreeTextException):
    pass


class UnknownInputException(FaultTreeTextException):
    pass


class InputCountException(FaultTreeTextException):
    pass


class CircularInputsException(FaultTreeTextException):
    pass


class DistributionSamplingError(FaultTreeTextException):
    pass


class InvalidProbabilityValueException(FaultTreeTextException):
    pass


class FaultTree:
    """
    Class representing a fault tree.
    """
    times: list[float]
    time_unit: str
    seed: str
    sample_size: int
    tolerance: float
    significant_figures: int
    scientific_exponent: int
    models: list['Model']
    events: list['Event']
    gates: list['Gate']
    computational_cache: ComputationalCache

    def __init__(self, fault_tree_text: str):
        # Parsing
        parsed_lines = parse_lines(fault_tree_text)
        parsed_paragraphs = parse_paragraphs(parsed_lines)
        parsed_assemblies = parse_assemblies(parsed_paragraphs)

        # Initialisation for main instantiation loop
        fault_tree_properties = {}
        models = []
        events = []
        gates = []
        seen_ids = set()
        event_index = 0

        # Main instantiation loop
        for parsed_assembly in parsed_assemblies:
            class_ = parsed_assembly.class_
            id_ = parsed_assembly.id_

            if id_ in seen_ids:
                raise DuplicateIdException(parsed_assembly.object_line.number, f'identifier `{id_}` already used')
            else:
                seen_ids.add(id_)

            if class_ == 'FaultTree':
                fault_tree_properties = parse_fault_tree_properties(parsed_assembly)
                continue

            if class_ == 'Model':
                model_properties = parse_model_properties(parsed_assembly)
                models.append(Model(id_, model_properties))
                continue

            if class_ == 'Event':
                event_properties = parse_event_properties(parsed_assembly)
                events.append(Event(id_, event_index, event_properties))
                event_index += 1
                continue

            if class_ == 'Gate':
                gate_properties = parse_gate_properties(parsed_assembly)
                gates.append(Gate(id_, gate_properties))
                continue

            raise ImplementationError(f'bad class {class_}')

        # Fault tree property extraction
        times = fault_tree_properties.get('times')
        time_unit = fault_tree_properties.get('time_unit')
        times_raw = fault_tree_properties.get('times_raw')
        times_line_number = fault_tree_properties.get('times_line_number')
        seed = fault_tree_properties.get('seed')
        sample_size = fault_tree_properties.get('sample_size', 1)
        sample_size_raw = fault_tree_properties.get('sample_size_raw')
        sample_size_line_number = fault_tree_properties.get('sample_size_line_number')
        tolerance = fault_tree_properties.get('tolerance', 0)
        tolerance_raw = fault_tree_properties.get('tolerance_raw')
        tolerance_line_number = fault_tree_properties.get('tolerance_line_number')
        significant_figures = fault_tree_properties.get('significant_figures', 3)
        significant_figures_raw = fault_tree_properties.get('significant_figures_raw')
        significant_figures_line_number = fault_tree_properties.get('significant_figures_line_number')
        scientific_exponent = fault_tree_properties.get('scientific_exponent', 3)
        scientific_exponent_raw = fault_tree_properties.get('scientific_exponent_raw')
        scientific_exponent_line_number = fault_tree_properties.get('scientific_exponent_line_number')
        unset_property_line_number = fault_tree_properties.get('unset_property_line_number', 1)

        # Identifier conveniences
        model_from_id = {model.id_: model for model in models}
        event_from_id = {event.id_: event for event in events}
        gate_from_id = {gate.id_: gate for gate in gates}
        all_used_model_ids = {event.model_id for event in events}
        all_input_ids = {
            input_id
            for gate in gates
            for input_id in gate.input_ids
        }

        # Validation
        FaultTree.validate_times(times, times_raw, times_line_number, unset_property_line_number)
        FaultTree.validate_sample_size(sample_size, sample_size_raw, sample_size_line_number)
        FaultTree.validate_tolerance(tolerance, tolerance_raw, tolerance_line_number)
        FaultTree.validate_significant_figures(significant_figures, significant_figures_raw,
                                               significant_figures_line_number)
        FaultTree.validate_scientific_exponent(scientific_exponent, scientific_exponent_raw,
                                               scientific_exponent_line_number)
        FaultTree.validate_event_models(event_from_id, model_from_id)
        FaultTree.validate_gate_inputs(event_from_id, gate_from_id)
        FaultTree.validate_cycle_free(gate_from_id)

        # Flattened indexing (flattened loop over times and samples)
        flattened_indexer = FlattenedIndexer(len(times), sample_size)
        flattened_size = flattened_indexer.flattened_size

        # Marking of objects
        FaultTree.mark_used_models(models, all_used_model_ids)
        FaultTree.mark_used_events(events, all_input_ids)
        FaultTree.mark_top_gates(gates, all_input_ids)

        # Enabling of flattened indexing
        FaultTree.enable_event_flattened_indexing(events, flattened_indexer)
        FaultTree.enable_gate_flattened_indexing(gates, flattened_indexer)

        # Finalisation of modelling
        FaultTree.determine_actual_model_types(events, model_from_id)
        FaultTree.generate_parameter_samples(events, model_from_id, seed, flattened_size)

        # Computation of expressions
        FaultTree.compute_event_expressions(events)
        FaultTree.compute_gate_expressions(event_from_id, gate_from_id)

        # Computation of event quantities
        FaultTree.compute_event_probabilities(events, times, sample_size)
        FaultTree.compute_event_intensities(events, times, sample_size)
        FaultTree.compute_event_rates(events)
        FaultTree.compute_event_expected_probabilities(events)
        FaultTree.compute_event_expected_intensities(events)
        FaultTree.compute_event_expected_rates(events)

        # Prepare cache for computation of gate quantities
        computational_cache = ComputationalCache(tolerance, events)

        # Computation of gate quantities
        FaultTree.compute_gate_probabilities(gates, computational_cache)
        FaultTree.compute_gate_intensities(gates, computational_cache)
        FaultTree.compute_gate_rates(gates)
        FaultTree.compute_gate_expected_probabilities(gates)
        FaultTree.compute_gate_expected_intensities(gates)
        FaultTree.compute_gate_expected_rates(gates)

        # Finalisation
        self.times = times
        self.time_unit = time_unit
        self.seed = seed
        self.sample_size = sample_size
        self.tolerance = tolerance
        self.significant_figures = significant_figures
        self.scientific_exponent = scientific_exponent
        self.models = models
        self.events = events
        self.gates = gates
        self.computational_cache = computational_cache

    def __repr__(self):
        return natural_repr(self)

    def compile_model_table(self) -> Table:
        headings = ['id', 'label', 'is_used']
        data = [
            [model.id_, model.label, model.is_used]
            for model in self.models
        ]
        return Table(headings, data)

    def compile_event_table(self) -> Table:
        headings = [
            'id', 'label', 'is_used',
            'time', 'sample',
            'computed_probability',
            'computed_intensity',
            'computed_rate',
        ]
        data = [
            [
                event.id_, event.label, event.is_used,
                time, sample_index,
                event.get_computed_probability(time_index, sample_index),
                event.get_computed_intensity(time_index, sample_index),
                event.get_computed_rate(time_index, sample_index),
            ]
            for event in self.events
            for time_index, time in enumerate(self.times)
            for sample_index in range(self.sample_size)
        ]
        return Table(headings, data)

    def compile_gate_table(self) -> Table:
        headings = [
            'id', 'label', 'is_top_gate', 'is_paged',
            'type', 'inputs',
            'time', 'sample',
            'computed_probability',
            'computed_intensity',
            'computed_rate',
        ]
        data = [
            [
                gate.id_, gate.label, gate.is_top_gate, gate.is_paged,
                gate.type_.name, ','.join(gate.input_ids),
                time, sample_index,
                gate.get_computed_probability(time_index, sample_index),
                gate.get_computed_intensity(time_index, sample_index),
                gate.get_computed_rate(time_index, sample_index),
            ]
            for gate in self.gates
            for time_index, time in enumerate(self.times)
            for sample_index in range(self.sample_size)
        ]
        return Table(headings, data)

    def compile_cut_set_tables(self) -> dict[str, Table]:
        return {
            gate.id_: gate.compile_cut_set_table(self.events, self.times, self.sample_size, self.computational_cache)
            for gate in self.gates
        }

    def compile_figures(self) -> dict[float, dict[str, Figure]]:
        return {
            time: {
                gate.id_: Figure(time_index, gate, fault_tree=self)
                for gate in self.gates
                if gate.is_top_gate or gate.is_paged
            }
            for time_index, time in enumerate(self.times)
        }

    @staticmethod
    def validate_times(times: list, times_raw: list, times_line_number: int, unset_property_line_number: int):
        if times is None:
            raise UnsetPropertyException(
                unset_property_line_number,
                'mandatory property `time` has not been set for fault tree (use `nan` for arbitrary time)',
            )

        for time, time_raw in zip(times, times_raw):
            if time < 0:
                raise NegativeValueException(times_line_number, f'negative time `{time_raw}`')

    @staticmethod
    def validate_sample_size(sample_size: int, sample_size_raw: str, sample_size_line_number: int):
        if sample_size < 1:
            raise SubUnitValueException(sample_size_line_number, f'sample size `{sample_size_raw}` less than unity')

    @staticmethod
    def validate_tolerance(tolerance: float, tolerance_raw: str, tolerance_line_number: int):
        if not 0 <= tolerance < 1:
            raise InvalidToleranceException(
                tolerance_line_number,
                f'tolerance `{tolerance_raw}` negative or not less than unity',
            )

    @staticmethod
    def validate_significant_figures(significant_figures: int, significant_figures_raw: str,
                                     significant_figures_line_number: int):
        if significant_figures < 1:
            raise SubUnitValueException(
                significant_figures_line_number,
                f'significant figures `{significant_figures_raw}` less than unity',
            )

    @staticmethod
    def validate_scientific_exponent(scientific_exponent: int, scientific_exponent_raw: str,
                                     scientific_exponent_line_number: int):
        if scientific_exponent < 0:
            raise NegativeValueException(
                scientific_exponent_line_number,
                f'negative scientific exponent `{scientific_exponent_raw}`',
            )

    @staticmethod
    def validate_event_models(event_from_id: dict[str, 'Event'], model_from_id: dict[str, 'Model']):
        for event in event_from_id.values():
            if event.model_id is None:
                continue

            if event.model_id not in model_from_id:
                raise UnknownModelException(event.model_id_line_number, f'no model with identifier `{event.model_id}`')

    @staticmethod
    def validate_gate_inputs(event_from_id: dict[str, 'Event'], gate_from_id: dict[str, 'Gate']):
        known_ids = [*event_from_id.keys(), *gate_from_id.keys()]
        for gate in gate_from_id.values():
            for input_id in gate.input_ids:
                if input_id not in known_ids:
                    raise UnknownInputException(
                        gate.input_ids_line_number,
                        f'no event or gate with identifier `{input_id}`',
                    )

            if gate.type_ == GateType.NULL and len(gate.input_ids) != 1:
                raise InputCountException(gate.input_ids_line_number, 'NULL gate must have exactly one input')

    @staticmethod
    def validate_cycle_free(gate_from_id: dict[str, 'Gate']):
        gate_ids = gate_from_id.keys()
        input_gate_ids_from_id = {
            id_: set.intersection(set(gate.input_ids), gate_ids)
            for id_, gate in gate_from_id.items()
        }

        if id_cycles := find_cycles(input_gate_ids_from_id):
            gate_cycle = [gate_from_id[id_] for id_ in min(id_cycles)]
            message = (
                'circular gate inputs detected: '
                + ' <-- '.join(f'`{gate.id_}` (line {gate.input_ids_line_number})' for gate in gate_cycle)
                + ' <-- ' + f'`{gate_cycle[0].id_}`'
            )
            raise CircularInputsException(None, message)

    @staticmethod
    def mark_used_models(models: list['Model'], all_used_model_ids: set[str]):
        for model in models:
            model.is_used = model.id_ in all_used_model_ids

    @staticmethod
    def mark_used_events(events: list['Event'], all_input_ids: set[str]):
        for event in events:
            event.is_used = event.id_ in all_input_ids

    @staticmethod
    def mark_top_gates(gates: list['Gate'], all_input_ids: set[str]):
        for gate in gates:
            gate.is_top_gate = gate.id_ not in all_input_ids

    @staticmethod
    def enable_event_flattened_indexing(events: list['Event'], flattened_indexer: 'FlattenedIndexer'):
        for event in events:
            event.flattened_indexer = flattened_indexer

    @staticmethod
    def enable_gate_flattened_indexing(gates: list['Gate'], flattened_indexer: 'FlattenedIndexer'):
        for gate in gates:
            gate.flattened_indexer = flattened_indexer

    @staticmethod
    def determine_actual_model_types(events: list['Event'], model_from_id: dict[str, 'Model']):
        for event in events:
            event.determine_actual_model_type(model_from_id)

    @staticmethod
    def generate_parameter_samples(events: list['Event'], model_from_id: dict[str, 'Model'],
                                   seed: str, flattened_size: int):
        random.seed(seed, version=2)

        for event in events:
            event.generate_parameter_samples(model_from_id, flattened_size)

    @staticmethod
    def compute_event_expressions(events: list['Event']):
        for event in events:
            event.compute_expression()

    @staticmethod
    def compute_gate_expressions(event_from_id: dict[str, 'Event'], gate_from_id: dict[str, 'Gate']):
        for gate in gate_from_id.values():
            gate.compute_expression(event_from_id, gate_from_id)

    @staticmethod
    def compute_event_probabilities(events: list['Event'], times: list[float], sample_size: int):
        for event in events:
            event.compute_probabilities(times, sample_size)

    @staticmethod
    def compute_event_intensities(events: list['Event'], times: list[float], sample_size: int):
        for event in events:
            event.compute_intensities(times, sample_size)

    @staticmethod
    def compute_event_rates(events: list['Event']):
        for event in events:
            event.compute_rates()

    @staticmethod
    def compute_event_expected_probabilities(events: list['Event']):
        for event in events:
            event.compute_expected_probabilities()

    @staticmethod
    def compute_event_expected_intensities(events: list['Event']):
        for event in events:
            event.compute_expected_intensities()

    @staticmethod
    def compute_event_expected_rates(events: list['Event']):
        for event in events:
            event.compute_expected_rates()

    @staticmethod
    def compute_gate_probabilities(gates: list['Gate'], computational_cache: ComputationalCache):
        for gate in gates:
            gate.compute_probabilities(computational_cache)

    @staticmethod
    def compute_gate_intensities(gates: list['Gate'], computational_cache: ComputationalCache):
        for gate in gates:
            gate.compute_intensities(computational_cache)

    @staticmethod
    def compute_gate_rates(gates: list['Gate']):
        for gate in gates:
            gate.compute_rates()

    @staticmethod
    def compute_gate_expected_probabilities(gates: list['Gate']):
        for gate in gates:
            gate.compute_expected_probabilities()

    @staticmethod
    def compute_gate_expected_intensities(gates: list['Gate']):
        for gate in gates:
            gate.compute_expected_intensities()

    @staticmethod
    def compute_gate_expected_rates(gates: list['Gate']):
        for gate in gates:
            gate.compute_expected_rates()


class Model:
    """
    Class representing a failure model (to be shared between multiple events).
    """
    id_: str
    label: str
    comment: str
    model_type: str
    model_dict: dict[str, Distribution]
    is_used: Optional[bool]

    def __init__(self, id_: str, properties: dict):
        label = properties.get('label')
        comment = properties.get('comment')
        model_type = properties.get('model_type')
        unset_property_line_number = properties.get('unset_property_line_number')

        model_dict = Model.extract_model_dict(properties)
        model_keys = list(model_dict)

        Model.validate_model_type_set(id_, model_type, unset_property_line_number)
        Model.validate_model_key_combo(id_, model_type, model_keys, unset_property_line_number)

        # Direct fields (from parameters or properties)
        self.id_ = id_
        self.label = label
        self.comment = comment

        # Indirect fields
        self.model_type = model_type
        self.model_dict = model_dict

        # Fields to be set by fault tree
        self.is_used = None

    def __repr__(self):
        return natural_repr(self)

    @staticmethod
    def extract_model_dict(properties: dict) -> dict[str, Distribution]:
        return {
            key: properties[key]
            for key in properties
            if key in VALID_MODEL_KEYS
        }

    @staticmethod
    def validate_model_type_set(id_: str, model_type: str, unset_property_line_number: int):
        if model_type is None:
            raise UnsetPropertyException(
                unset_property_line_number,
                f'mandatory property `model_type` has not been set for model `{id_}`',
            )

    @staticmethod
    def validate_model_key_combo(id_: str, model_type: str, model_keys: list[str], unset_property_line_number: int):
        model_key_set = set(model_keys)
        valid_key_sets = [
            set(combo)
            for combo in VALID_KEY_COMBOS_FROM_MODEL_TYPE[model_type]
        ]

        if model_key_set not in valid_key_sets:
            message = (
                f'invalid model key combination '
                f'{{{natural_join_backticks(model_keys, penultimate_separator=None)}}} for model `{id_}`'
            )
            explainer = '\n'.join([
                f'Recognised key combinations for model type `{model_type}` are:',
                *[
                    f'- {{{natural_join_backticks(combo, penultimate_separator=None)}}}'
                    for combo in VALID_KEY_COMBOS_FROM_MODEL_TYPE[model_type]
                ]
            ])

            raise InvalidModelKeyComboException(unset_property_line_number, message, explainer)

    @staticmethod
    def generate_parameter_samples(model_dict: dict[str, Distribution], flattened_size: int) -> dict[str, list[float]]:
        samples_from_parameter = {}

        for parameter, distribution in model_dict.items():
            try:
                samples = distribution.generate_samples(flattened_size)
            except (ValueError, OverflowError) as exception:
                raise DistributionSamplingError(
                    distribution.line_number,
                    f'`{exception.__class__.__name__}` raised whilst sampling from `{distribution}`:',
                    traceback.format_exc(),
                )

            try:
                Model.validate_samples(parameter, samples)
            except (InvalidProbabilityValueException, NegativeValueException) as exception:
                raise exception.__class__(
                    distribution.line_number,
                    f'{exception.message} whilst sampling from `{distribution}`:',
                )

            samples_from_parameter[parameter] = samples

        return samples_from_parameter

    @staticmethod
    def validate_samples(parameter: str, samples: list[float]):
        if parameter == 'probability':
            try:
                bad_value = next(value for value in samples if value < 0 or value > 1)
            except StopIteration:
                return

            raise InvalidProbabilityValueException(None, f'invalid `probability` value `{bad_value}` encountered')

        if parameter in ('intensity', 'failure_rate', 'repair_rate', 'mean_repair_time', 'mean_failure_time'):
            try:
                bad_value = next(value for value in samples if value < 0)
            except StopIteration:
                return

            raise NegativeValueException(None, f'negative `{parameter}` value `{bad_value}` encountered')

        raise ImplementationError(f'bad parameter `{parameter}`')


class Object:
    """
    Superclass representing computational behaviour shared between events and gates.
    """
    id_: Optional[str]
    label: Optional[str]
    comment: Optional[str]

    flattened_indexer: Optional['FlattenedIndexer']
    computed_expression: Optional[Expression]
    computed_probabilities: Optional[list[float]]
    computed_intensities: Optional[list[float]]
    computed_rates: Optional[list[float]]
    computed_expected_probabilities: Optional[list[float]]
    computed_expected_intensities: Optional[list[float]]
    computed_expected_rates: Optional[list[float]]

    def __init__(self, id_: str, label: Optional[str], comment: Optional[str]):
        # Direct fields (from parameters or properties)
        self.id_ = id_
        self.label = label
        self.comment = comment

        # Fields to be set by fault tree
        self.flattened_indexer = None
        self.computed_expression = None
        self.computed_probabilities = None
        self.computed_intensities = None
        self.computed_rates = None
        self.computed_expected_probabilities = None
        self.computed_expected_intensities = None
        self.computed_expected_rates = None

    def __lt__(self, other):
        return self.id_ < other.id_

    def __repr__(self):
        return natural_repr(self)

    @memoise('computed_rates')
    def compute_rates(self) -> list[float]:
        return [
            robust_divide(omega, 1 - q)
            for q, omega in zip(self.computed_probabilities, self.computed_intensities)
        ]

    @memoise('computed_expected_probabilities')
    def compute_expected_probabilities(self) -> list[float]:
        return [
            statistics.mean(self.computed_probabilities[self.flattened_indexer.get_slice(time_index)])
            for time_index in range(self.flattened_indexer.time_count)
        ]

    @memoise('computed_expected_intensities')
    def compute_expected_intensities(self) -> list[float]:
        return [
            statistics.mean(self.computed_intensities[self.flattened_indexer.get_slice(time_index)])
            for time_index in range(self.flattened_indexer.time_count)
        ]

    @memoise('computed_expected_rates')
    def compute_expected_rates(self) -> list[float]:
        return [
            statistics.mean(self.computed_rates[self.flattened_indexer.get_slice(time_index)])
            for time_index in range(self.flattened_indexer.time_count)
        ]

    def get_computed_probability(self, time_index: int, sample_index: int) -> float:
        flattened_index = self.flattened_indexer.get_index(time_index, sample_index)
        return self.computed_probabilities[flattened_index]

    def get_computed_intensity(self, time_index: int, sample_index: int) -> float:
        flattened_index = self.flattened_indexer.get_index(time_index, sample_index)
        return self.computed_intensities[flattened_index]

    def get_computed_rate(self, time_index: int, sample_index: int) -> float:
        flattened_index = self.flattened_indexer.get_index(time_index, sample_index)
        return self.computed_rates[flattened_index]


class Event(Object):
    """
    Class representing a primary event.
    """
    id_: Optional[str]
    index: int
    label: Optional[str]
    comment: Optional[str]
    model_id: str
    model_id_line_number: int
    appearance: EventAppearance

    model_type: str
    model_dict: dict[str, Distribution]

    is_used: Optional[bool]
    actual_model_type: Optional[str]
    parameter_samples: Optional[dict[str, list[float]]]

    def __init__(self, id_: str, index: int, properties: dict):
        label = properties.get('label')
        comment = properties.get('comment')
        model_type = properties.get('model_type')
        model_id = properties.get('model_id')
        model_id_line_number = properties.get('model_id_line_number')
        appearance = properties.get('appearance', EventAppearance.BASIC)
        unset_property_line_number = properties.get('unset_property_line_number')

        model_dict = Model.extract_model_dict(properties)
        model_keys = list(model_dict)

        Event.validate_model_xor_type_set(id_, model_type, model_id, unset_property_line_number)
        Event.validate_model_key_combo(id_, model_type, model_keys, unset_property_line_number)

        # Direct fields (from parameters or properties)
        self.id_ = None  # placeholder assigned here for __dict__ order; to be reassigned by super()
        self.index = index
        self.label = None  # placeholder assigned here for __dict__ order; to be reassigned by super()
        self.comment = None  # placeholder assigned here for __dict__ order; to be reassigned by super()
        self.model_id = model_id
        self.model_id_line_number = model_id_line_number
        self.appearance = appearance

        # Indirect fields
        self.model_type = model_type
        self.model_dict = model_dict

        # Fields to be set by fault tree
        self.is_used = None
        self.flattened_indexer = None  # placeholder assigned here for __dict__ order; to be reassigned by super()
        self.actual_model_type = None
        self.parameter_samples = None

        # Fields shared with class Gate
        super().__init__(id_, label, comment)

    @memoise('actual_model_type')
    def determine_actual_model_type(self, model_from_id: dict[str, Model]) -> str:
        model_owner = model_from_id.get(self.model_id, self)
        return model_owner.model_type

    @memoise('parameter_samples')
    def generate_parameter_samples(self, model_from_id: dict[str, Model],
                                   flattened_size: int) -> dict[str, list[float]]:
        model_owner = model_from_id.get(self.model_id, self)
        model_dict = model_owner.model_dict

        return Model.generate_parameter_samples(model_dict, flattened_size)

    @memoise('computed_expression')
    def compute_expression(self) -> Expression:
        if self.actual_model_type == 'True':
            return Expression(Term(encoding=0))

        if self.actual_model_type == 'False':
            return Expression()

        return Expression(Term.create_from_event_index(self.index))

    @memoise('computed_probabilities')
    def compute_probabilities(self, times: list[float], sample_size: int) -> list[float]:
        if self.actual_model_type == 'Fixed':
            return self.parameter_samples['probability']

        if self.actual_model_type == 'True':
            return [1 for _ in range(len(times) * sample_size)]

        if self.actual_model_type == 'False':
            return [0 for _ in range(len(times) * sample_size)]

        time_values = [t for t in times for _ in range(sample_size)]

        if self.actual_model_type == 'ConstantRate':
            try:
                failure_rate_samples = self.parameter_samples['failure_rate']
            except KeyError:
                failure_rate_samples = [robust_invert(x) for x in self.parameter_samples['mean_failure_time']]

            try:
                repair_rate_samples = self.parameter_samples['repair_rate']
            except KeyError:
                repair_rate_samples = [robust_invert(x) for x in self.parameter_samples['mean_repair_time']]

            return [
                constant_rate_model_probability(t, lambda_, mu)
                for t, lambda_, mu in zip(time_values, failure_rate_samples, repair_rate_samples)
            ]

        raise ImplementationError(f'bad actual_model_type {self.actual_model_type}')

    @memoise('computed_intensities')
    def compute_intensities(self, times: list[float], sample_size: int) -> list[float]:
        if self.actual_model_type == 'Fixed':
            return self.parameter_samples['intensity']

        if self.actual_model_type in ('True', 'False'):
            return [0 for _ in range(len(times) * sample_size)]

        time_values = [t for t in times for _ in range(sample_size)]

        if self.actual_model_type == 'ConstantRate':
            try:
                failure_rate_samples = self.parameter_samples['failure_rate']
            except KeyError:
                failure_rate_samples = [robust_invert(x) for x in self.parameter_samples['mean_failure_time']]

            try:
                repair_rate_samples = self.parameter_samples['repair_rate']
            except KeyError:
                repair_rate_samples = [robust_invert(x) for x in self.parameter_samples['mean_repair_time']]

            return [
                constant_rate_model_intensity(t, lambda_, mu)
                for t, lambda_, mu in zip(time_values, failure_rate_samples, repair_rate_samples)
            ]

        raise ImplementationError(f'bad actual_model_type {self.actual_model_type}')

    @staticmethod
    def validate_model_xor_type_set(id_: str, model_type: str, model_id: str, unset_property_line_number: int):
        is_model_type_set = model_type is not None
        is_model_set = model_id is not None

        if is_model_type_set and is_model_set:
            raise ModelPropertyClashException(
                unset_property_line_number,
                f'both `model_type` and `model` have been set for event `{id_}`',
            )

        if not is_model_type_set and not is_model_set:
            raise UnsetPropertyException(
                unset_property_line_number,
                f'one of `model_type` or `model` has not been set for event `{id_}`',
            )

    @staticmethod
    def validate_model_key_combo(id_: str, model_type: str, model_keys: list[str], unset_property_line_number: int):
        if model_type is None:
            if model_keys:
                message = (
                    f'both `model` and model keys '
                    f'{{{natural_join_backticks(model_keys, penultimate_separator=None)}}} '
                    f'have been set for event `{id_}`'
                )
                raise ModelPropertyClashException(unset_property_line_number, message)
            else:
                return

        model_key_set = set(model_keys)
        valid_key_sets = [
            set(combo)
            for combo in VALID_KEY_COMBOS_FROM_MODEL_TYPE[model_type]
        ]

        if model_key_set not in valid_key_sets:
            message = (
                f'invalid model key combination '
                f'{{{natural_join_backticks(model_keys, penultimate_separator=None)}}} for event `{id_}`'
            )
            explainer = '\n'.join([
                f'Recognised key combinations for model type `{model_type}` are:',
                *[
                    f'- {{{natural_join_backticks(combo, penultimate_separator=None)}}}'
                    for combo in VALID_KEY_COMBOS_FROM_MODEL_TYPE[model_type]
                ]
            ])

            raise InvalidModelKeyComboException(unset_property_line_number, message, explainer)


class Gate(Object):
    """
    Class representing a gate.
    """
    id_: Optional[str]
    label: Optional[str]
    is_paged: bool
    type_: GateType
    vote_threshold: Optional[int]
    input_ids: list[str]
    input_ids_line_number: int
    comment: Optional[str]

    is_top_gate: Optional[bool]

    def __init__(self, id_: str, properties: dict):
        label = properties.get('label')
        is_paged = properties.get('is_paged', False)
        type_ = properties.get('type')
        vote_threshold = properties.get('vote_threshold')
        input_ids = properties.get('input_ids')
        input_ids_line_number = properties.get('input_ids_line_number')
        comment = properties.get('comment')
        unset_property_line_number = properties.get('unset_property_line_number')

        Gate.validate_type_set(id_, type_, unset_property_line_number)
        Gate.validate_input_ids_set(id_, input_ids, unset_property_line_number)

        # Direct fields (from parameters or properties)
        self.id_ = None  # placeholder assigned here for __dict__ order; to be reassigned by super()
        self.label = None  # placeholder assigned here for __dict__ order; to be reassigned by super()
        self.is_paged = is_paged
        self.type_ = type_
        self.vote_threshold = vote_threshold
        self.input_ids = input_ids
        self.input_ids_line_number = input_ids_line_number
        self.comment = None  # placeholder assigned here for __dict__ order; to be reassigned by super()

        # Fields to be set by fault tree
        self.is_top_gate = None

        # Fields shared with class Event
        super().__init__(id_, label, comment)

    @memoise('computed_expression')
    def compute_expression(self, event_from_id: dict[str, 'Event'], gate_from_id: dict[str, 'Gate']) -> Expression:
        object_from_id = {**event_from_id, **gate_from_id}
        input_expressions = [
            object_from_id[input_id].compute_expression(event_from_id, gate_from_id)
            for input_id in self.input_ids
        ]

        if self.type_ == GateType.NULL:
            return input_expressions[0]

        if self.type_ == GateType.AND:
            return Expression.conjunction(*input_expressions)

        if self.type_ == GateType.OR:
            return Expression.disjunction(*input_expressions)

        if self.type_ == GateType.VOTE:
            return Expression.vote(*input_expressions, threshold=self.vote_threshold)

        raise ImplementationError(f'bad gate type `{self.type_}`')

    @memoise('computed_probabilities')
    def compute_probabilities(self, computational_cache: ComputationalCache) -> list[float]:
        return [
            disjunction_probability(self.computed_expression.terms, flattened_index, computational_cache)
            for flattened_index in range(self.flattened_indexer.flattened_size)
        ]

    @memoise('computed_intensities')
    def compute_intensities(self, computational_cache: ComputationalCache) -> list[float]:
        return [
            disjunction_intensity(self.computed_expression.terms, flattened_index, computational_cache)
            for flattened_index in range(self.flattened_indexer.flattened_size)
        ]

    def compile_cut_set_table(self, events: list[Event], times: list[float], sample_size: int,
                              computational_cache: ComputationalCache) -> Table:
        headings = [
            'cut_set',
            'order',
            'time', 'sample',
            'computed_probability',
            'computed_intensity',
            'computed_rate',
            'probability_importance',
            'intensity_importance',
        ]

        terms = self.computed_expression.terms
        flattened_index = self.flattened_indexer.get_index

        q = computational_cache.probability
        omega = computational_cache.intensity
        lambda_ = computational_cache.rate

        data = [
            [
                format_cut_set(tuple(events[index].id_ for index in term.event_indices())),
                term.order(),
                time, sample_index,
                q_term := q(term, i := flattened_index(time_index, sample_index)),
                omega_term := omega(term, i),
                lambda_(term, i),
                robust_divide(q_term, sum(q(c, i) for c in terms)),
                robust_divide(omega_term, sum(omega(c, i) for c in terms)),
            ]
            for term in sorted(terms)
            for time_index, time in enumerate(times)
            for sample_index in range(sample_size)
        ]
        return Table(headings, data)

    @staticmethod
    def validate_type_set(id_: str, type_: LineType, unset_property_line_number: int):
        if type_ is None:
            raise UnsetPropertyException(
                unset_property_line_number,
                f'mandatory property `type` has not been set for gate `{id_}`',
            )

    @staticmethod
    def validate_input_ids_set(id_: str, input_ids: list, unset_property_line_number: int):
        if input_ids is None:
            raise UnsetPropertyException(
                unset_property_line_number,
                f'mandatory property `inputs` has not been set for gate `{id_}`',
            )


class FlattenedIndexer:
    """
    Flattened indexer, to be used by objects whose results are stored in flattened lists.

    Flattened lists of results are of length `time_count * sample_size`,
    and effectively indexed by the following comprehension:
    [
        (flattened_index := time_index * sample_size + sample_index)
        for time_index in range(time_count)
        for sample_index in range(sample_size)
    ]
    """
    time_count: int
    sample_size: int
    flattened_size: int

    def __init__(self, time_count: int, sample_size: int):
        self.time_count = time_count
        self.sample_size = sample_size
        self.flattened_size = time_count * sample_size

    def __repr__(self):
        return natural_repr(self)

    def get_index(self, time_index: int, sample_index: int) -> int:
        if not 0 <= time_index < self.time_count:
            raise IndexError(f'time_index {time_index} is out of bounds')

        if not 0 <= sample_index < self.sample_size:
            raise IndexError(f'sample_index {sample_index} is out of bounds')

        return time_index * self.sample_size + sample_index

    def get_slice(self, time_index: int) -> slice:  # flattened indices for a given time_index are consecutive
        if not 0 <= time_index < self.time_count:
            raise IndexError(f'time_index {time_index} is out of bounds')

        start = time_index * self.sample_size
        end = (time_index + 1) * self.sample_size

        return slice(start, end)
