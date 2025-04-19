"""
# Public Fault Tree Analyser: core.py

Core fault tree analysis classes.

**Copyright 2025 Conway.**
Licensed under the GNU General Public License v3.0 (GPL-3.0-only).
This is free software with NO WARRANTY etc. etc., see LICENSE.
"""

from pfta.common import natural_repr
from pfta.parsing import (
    UnsetPropertyException,
    parse_lines, parse_paragraphs, parse_assemblies, parse_fault_tree_properties,
)
from pfta.woe import ImplementationError


class FaultTree:
    def __init__(self, fault_tree_text: str):
        parsed_lines = parse_lines(fault_tree_text)
        parsed_paragraphs = parse_paragraphs(parsed_lines)
        parsed_assemblies = parse_assemblies(parsed_paragraphs)

        time_unit = None
        times = None

        for parsed_assembly in parsed_assemblies:
            class_ = parsed_assembly.class_
            id_ = parsed_assembly.id_

            if class_ == 'FaultTree':
                fault_tree_properties = parse_fault_tree_properties(parsed_assembly)

                try:
                    time_unit = fault_tree_properties['time_unit']
                except KeyError:
                    pass

                try:
                    times = fault_tree_properties['times']
                except KeyError:
                    pass

                continue

            if class_ == 'Event':
                # TODO
                continue

            if class_ == 'Gate':
                # TODO
                continue

            raise ImplementationError(f'bad class {class_}')

        if times is None:
            if parsed_assemblies and parsed_assemblies[0].class_ == 'FaultTree':
                unset_times_line_number = parsed_assemblies[0].last_line_number() + 1
            else:
                unset_times_line_number = 1

            raise UnsetPropertyException(
                unset_times_line_number,
                'mandatory property `time` has not been set for fault tree',
            )

        self.time_unit = time_unit
        self.times = times

    def __repr__(self):
        return natural_repr(self)
