"""
# Public Fault Tree Analyser: core.py

Core fault tree analysis classes.

**Copyright 2025 Conway.**
Licensed under the GNU General Public License v3.0 (GPL-3.0-only).
This is free software with NO WARRANTY etc. etc., see LICENSE.
"""

import traceback

from pfta.boolean import Term, Expression
from pfta.common import natural_repr, format_cut_set, natural_join_backticks
from pfta.constants import LineType, GateType, VALID_KEY_COMBOS_FROM_MODEL_TYPE, VALID_MODEL_KEYS
from pfta.parsing import (
    parse_lines, parse_paragraphs, parse_assemblies,
    parse_fault_tree_properties, parse_model_properties, parse_event_properties, parse_gate_properties,
)
from pfta.presentation import Table
from pfta.sampling import Distribution
from pfta.utilities import find_cycles
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


class UnknownModelException(FaultTreeTextException):
    pass


class UnknownInputException(FaultTreeTextException):
    pass


class CircularInputsException(FaultTreeTextException):
    pass


class DistributionSamplingError(FaultTreeTextException):
    pass


class FaultTree:
    """
    Class representing a fault tree.
    """
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
        time_unit = fault_tree_properties.get('time_unit')
        times = fault_tree_properties.get('times')
        times_raw = fault_tree_properties.get('times_raw')
        times_line_number = fault_tree_properties.get('times_line_number')
        seed = fault_tree_properties.get('seed')
        sample_size = fault_tree_properties.get('sample_size', 1)
        sample_size_raw = fault_tree_properties.get('sample_size_raw')
        sample_size_line_number = fault_tree_properties.get('sample_size_line_number')
        unset_property_line_number = fault_tree_properties.get('unset_property_line_number', 1)

        # Identifier conveniences
        model_from_id = {model.id_: model for model in models}
        event_from_id = {event.id_: event for event in events}
        gate_from_id = {gate.id_: gate for gate in gates}
        all_input_ids = {
            input_id
            for gate in gates
            for input_id in gate.input_ids
        }

        # Validation
        FaultTree.validate_times(times, times_raw, times_line_number, unset_property_line_number)
        FaultTree.validate_sample_size(sample_size, sample_size_raw, sample_size_line_number)
        FaultTree.validate_event_models(event_from_id, model_from_id)
        FaultTree.validate_gate_inputs(event_from_id, gate_from_id)
        FaultTree.validate_cycle_free(gate_from_id)

        # Marking of objects
        FaultTree.mark_used_events(events, all_input_ids)
        FaultTree.mark_top_gates(gates, all_input_ids)

        # Sampling of distributions
        FaultTree.sample_model_distributions(models, times, sample_size)

        # Computation of expressions
        FaultTree.compute_event_expressions(events)
        FaultTree.compute_gate_expressions(event_from_id, gate_from_id)

        # Computation of quantities
        # TODO: compute quantities over times and samples

        # Finalisation
        self.time_unit = time_unit
        self.times = times
        self.seed = seed
        self.sample_size = sample_size
        self.models = models
        self.events = events
        self.gates = gates

    def __repr__(self):
        return natural_repr(self)

    def compile_event_table(self) -> Table:
        headings = ['index', 'id', 'is_used', 'label', 'comment']  # TODO: computed quantities
        data = [
            [event.index, event.id_, event.is_used, event.label, event.comment]
            for event in self.events
            # TODO: time dependence and sample number dependence
        ]
        return Table(headings, data)

    def compile_gate_table(self) -> Table:
        headings = [
            'id', 'is_top_gate', 'is_paged',
            'type', 'inputs',
            # TODO: computed quantities
            'label', 'comment',
        ]
        data = [
            [
                gate.id_, gate.is_top_gate, gate.is_paged,
                gate.type_.name, ','.join(gate.input_ids),
                gate.label, gate.comment,
            ]
            for gate in self.gates
            # TODO: time dependence and sample number dependence
        ]
        return Table(headings, data)

    def compile_cut_set_tables(self) -> dict[str, Table]:
        return {
            gate.id_: gate.compile_cut_set_table(self.events)
            for gate in self.gates
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
            raise SubUnitValueException(sample_size_line_number, f'sample size {sample_size_raw} less than unity')

    @staticmethod
    def validate_event_models(event_from_id: dict[str, 'Event'], model_from_id: dict[str, 'Model']):
        for event in event_from_id.values():
            if event.model_id is None:
                continue

            if event.model_id not in model_from_id.keys():
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
    def mark_used_events(events: list['Event'], all_input_ids: set[str]):
        for event in events:
            event.is_used = event.id_ in all_input_ids

    @staticmethod
    def mark_top_gates(gates: list['Gate'], all_input_ids: set[str]):
        for gate in gates:
            gate.is_top_gate = gate.id_ not in all_input_ids

    @staticmethod
    def sample_model_distributions(models: list['Model'], times: list[float], sample_size: int):
        for model in models:
            model.sample_distributions(times, sample_size)

    @staticmethod
    def compute_event_expressions(events: list['Event']):
        for event in events:
            event.compute_expression()

    @staticmethod
    def compute_gate_expressions(event_from_id: dict[str, 'Event'], gate_from_id: dict[str, 'Gate']):
        for gate in gate_from_id.values():
            gate.compute_expression(event_from_id, gate_from_id)


class Model:
    """
    Class representing a failure model (to be shared between multiple events).
    """
    def __init__(self, id_: str, properties: dict):
        label = properties.get('label')
        comment = properties.get('comment')
        model_type = properties.get('model_type')
        unset_property_line_number = properties.get('unset_property_line_number')

        model_properties = Model.extract_model_subset(properties)
        model_keys = list(model_properties.keys())

        Model.validate_model_type_set(id_, model_type, unset_property_line_number)
        Model.validate_model_key_combo(id_, model_type, model_keys, unset_property_line_number)

        # Direct fields (from parameters or properties)
        self.id_ = id_
        self.label = label
        self.comment = comment

        # Indirect fields
        self.model_type = model_type
        self.model_properties = model_properties

        # Fields to be set by fault tree
        self.model_samples = None

    def __repr__(self):
        return natural_repr(self)

    @memoise('model_samples')
    def sample_distributions(self, times: list[float], sample_size: int) -> dict[str, dict[float, list[float]]]:
        samples_from_time_from_parameter = {}

        for parameter, distribution in self.model_properties.items():
            try:
                samples_from_time = {
                    time: distribution.generate_samples(sample_size)
                    for time in times
                }
            except (ValueError, OverflowError) as exception:
                raise DistributionSamplingError(
                    distribution.line_number,
                    f'`{exception.__class__.__name__}` raised whilst sampling from `{distribution}`:',
                    traceback.format_exc(),
                )

            samples_from_time_from_parameter[parameter] = samples_from_time

        return samples_from_time_from_parameter

    @staticmethod
    def extract_model_subset(properties: dict) -> dict[str, Distribution]:
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


class Event:
    """
    Class representing a primary event.
    """
    def __init__(self, id_: str, index: int, properties: dict):
        label = properties.get('label')
        comment = properties.get('comment')
        model_type = properties.get('model_type')
        model_id = properties.get('model_id')
        model_id_line_number = properties.get('model_id_line_number')
        unset_property_line_number = properties.get('unset_property_line_number')

        model_properties = Model.extract_model_subset(properties)
        model_keys = list(model_properties.keys())

        Event.validate_model_xor_type_set(id_, model_type, model_id, unset_property_line_number)
        Event.validate_model_key_combo(id_, model_type, model_keys, unset_property_line_number)
        # TODO: validate probability and intensity values valid (when evaluated at times across sample size)

        # Direct fields (from parameters or properties)
        self.id_ = id_
        self.index = index
        self.label = label
        self.comment = comment
        self.model_id = model_id
        self.model_id_line_number = model_id_line_number

        # Indirect fields
        self.model_type = model_type
        self.model_properties = model_properties

        # Fields to be set by fault tree
        self.is_used = None
        self.computed_expression = None

    def __repr__(self):
        return natural_repr(self)

    @memoise('computed_expression')
    def compute_expression(self) -> Expression:
        encoding = 1 << self.index
        return Expression(Term(encoding))

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


class Gate:
    """
    Class representing a gate.
    """
    def __init__(self, id_: str, properties: dict):
        label = properties.get('label')
        is_paged = properties.get('is_paged', False)
        type_ = properties.get('type')
        input_ids = properties.get('input_ids')
        input_ids_line_number = properties.get('input_ids_line_number')
        comment = properties.get('comment')
        unset_property_line_number = properties.get('unset_property_line_number')

        Gate.validate_type_set(id_, type_, unset_property_line_number)
        Gate.validate_input_ids_set(id_, input_ids, unset_property_line_number)

        # Direct fields (from parameters or properties)
        self.id_ = id_
        self.label = label
        self.is_paged = is_paged
        self.type_ = type_
        self.input_ids = input_ids
        self.input_ids_line_number = input_ids_line_number
        self.comment = comment

        # Fields to be set by fault tree
        self.is_top_gate = None
        self.computed_expression = None

    def __repr__(self):
        return natural_repr(self)

    @memoise('computed_expression')
    def compute_expression(self, event_from_id: dict[str, 'Event'], gate_from_id: dict[str, 'Gate']) -> Expression:
        object_from_id = {**event_from_id, **gate_from_id}
        input_expressions = [
            object_from_id[input_id].compute_expression(event_from_id, gate_from_id)
            for input_id in self.input_ids
        ]

        if self.type_ == GateType.AND:
            boolean_operator = Expression.conjunction
        elif self.type_ == GateType.OR:
            boolean_operator = Expression.disjunction
        else:
            raise ImplementationError(f'bad gate type `{self.type_}`')

        return boolean_operator(*input_expressions)

    def compile_cut_set_table(self, events: list[Event]) -> Table:
        headings = [
            'cut_set',
            'order',
            # TODO: computed quantities
        ]
        data = [
            [
                format_cut_set(events[index].id_ for index in term.event_indices()),
                term.order(),
            ]
            for term in sorted(self.computed_expression.terms)
            # TODO: time dependence and sample number dependence
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
