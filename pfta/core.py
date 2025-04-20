"""
# Public Fault Tree Analyser: core.py

Core fault tree analysis classes.

**Copyright 2025 Conway.**
Licensed under the GNU General Public License v3.0 (GPL-3.0-only).
This is free software with NO WARRANTY etc. etc., see LICENSE.
"""

from pfta.common import natural_repr
from pfta.parsing import (
    parse_lines, parse_paragraphs, parse_assemblies,
    parse_fault_tree_properties, parse_event_properties, parse_gate_properties,
)
from pfta.woe import ImplementationError, FaultTreeTextException


class DuplicateIdException(FaultTreeTextException):
    pass


class UnsetPropertyException(FaultTreeTextException):
    pass


class NonPositiveValueException(FaultTreeTextException):
    pass


class SubUnitValueException(FaultTreeTextException):
    pass


class FaultTree:
    def __init__(self, fault_tree_text: str):
        parsed_lines = parse_lines(fault_tree_text)
        parsed_paragraphs = parse_paragraphs(parsed_lines)
        parsed_assemblies = parse_assemblies(parsed_paragraphs)

        fault_tree_properties = {}
        events = []
        gates = []
        seen_ids = set()
        event_index = 0

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

        time_unit = fault_tree_properties.get('time_unit')
        times = fault_tree_properties.get('times')
        times_raw = fault_tree_properties.get('times_raw')
        times_line_number = fault_tree_properties.get('times_line_number')
        seed = fault_tree_properties.get('seed')
        sample_size = fault_tree_properties.get('sample_size', 1)
        sample_size_raw = fault_tree_properties.get('sample_size_raw')
        sample_size_line_number = fault_tree_properties.get('sample_size_line_number')
        unset_property_line_number = fault_tree_properties.get('unset_property_line_number', 1)

        if times is None:
            raise UnsetPropertyException(
                unset_property_line_number,
                'mandatory property `time` has not been set for fault tree',
            )

        for time, time_raw in zip(times, times_raw):
            if time <= 0:
                raise NonPositiveValueException(times_line_number, f'non-positive time `{time_raw}`')

        if sample_size < 1:
            raise SubUnitValueException(sample_size_line_number, f'sample size {sample_size_raw} less than unity')

        self.time_unit = time_unit
        self.times = times
        self.seed = seed
        self.sample_size = sample_size
        self.events = events
        self.gates = gates

    def __repr__(self):
        return natural_repr(self)


class Event:
    def __init__(self, id_: str, event_index: int, event_properties: dict):
        label = event_properties.get('label')
        probability = event_properties.get('probability')
        intensity = event_properties.get('intensity')
        comment = event_properties.get('comment')

        # TODO: check probability and intensity values valid (when evaluated at times across sample size)

        self.id_ = id_
        self.event_index = event_index
        self.label = label
        self.probability = probability
        self.intensity = intensity
        self.comment = comment

    def __repr__(self):
        return natural_repr(self)


class Gate:
    def __init__(self, id_: str, gate_properties: dict):
        label = gate_properties.get('label')
        is_paged = gate_properties.get('is_paged', False)
        type_ = gate_properties.get('type')
        input_ids = gate_properties.get('input_ids')
        comment = gate_properties.get('comment')
        unset_property_line_number = gate_properties.get('unset_property_line_number')

        if type_ is None:
            raise UnsetPropertyException(
                unset_property_line_number,
                f'mandatory property `type` has not been set for gate `{id_}`',
            )

        if input_ids is None:
            raise UnsetPropertyException(
                unset_property_line_number,
                f'mandatory property `inputs` has not been set for gate `{id_}`',
            )

        self.id_ = id_
        self.label = label
        self.is_paged = is_paged
        self.type_ = type_
        self.input_ids = input_ids
        self.comment = comment

    def __repr__(self):
        return natural_repr(self)
