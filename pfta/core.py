"""
# Public Fault Tree Analyser: core.py

Core fault tree analysis classes.

**Copyright 2025 Conway**
Licensed under the GNU General Public License v3.0 (GPL-3.0-only).
This is free software with NO WARRANTY etc. etc., see LICENSE.
"""

from pfta.parsing import parse_lines


class FaultTree:
    def __init__(self, fault_tree_text: str):
        parsed_lines = parse_lines(fault_tree_text)

        events = []
        gates = []

        current_event_index = 0
        current_object_class = FaultTree
        used_ids = set()

        for parsed_line in parsed_lines:
            pass  # TODO: move this to building.py(?) and separately have computing
