"""
# Public Fault Tree Analyser: core.py

Core fault tree analysis classes.

**Copyright 2025 Conway**
Licensed under the GNU General Public License v3.0 (GPL-3.0-only).
This is free software with NO WARRANTY etc. etc., see LICENSE.
"""

from pfta.parsing import DanglingPropertyException
from pfta.parsing import parse_lines, parse_paragraphs


class FaultTree:
    def __init__(self, fault_tree_text: str):
        parsed_lines = parse_lines(fault_tree_text)
        parsed_paragraphs = parse_paragraphs(parsed_lines)

        events = []
        gates = []

        current_event_index = 0
        used_ids = set()

        for parsed_paragraph in parsed_paragraphs:
            object_line = parsed_paragraph.object_line
            property_lines = parsed_paragraph.property_lines

            if object_line is None:
                if parsed_paragraph == parsed_paragraphs[0]:
                    # TODO: set fault tree properties
                    continue

                raise DanglingPropertyException(
                    property_lines[0].number,
                    f'missing object declaration before setting property `{property_lines[0].info["key"]}`',
                )

            if object_line.info['class_'] == 'Event':
                # TODO: construct event
                continue

            if object_line.info['class_'] == 'Gate':
                # TODO: construct gate
                continue

            # TODO: raise invalid class exception
