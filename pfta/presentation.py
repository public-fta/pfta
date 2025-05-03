"""
# Public Fault Tree Analyser: presentation.py

Presentational classes.

**Copyright 2025 Conway.**
Licensed under the GNU General Public License v3.0 (GPL-3.0-only).
This is free software with NO WARRANTY etc. etc., see LICENSE.
"""

import csv
import os
from typing import TYPE_CHECKING, Optional

from pfta.common import natural_repr
from pfta.woe import ImplementationError

if TYPE_CHECKING:
    from pfta.core import FaultTree, Event, Gate


EVENT_BOUNDING_WIDTH = 120
EVENT_BOUNDING_HEIGHT = 210


class Figure:
    """
    Class representing a figure (a page of a fault tree).
    """
    def __init__(self, gate: 'Gate', fault_tree: 'FaultTree'):
        event_from_id = {event.id_: event for event in fault_tree.events}
        gate_from_id = {gate.id_: gate for gate in fault_tree.gates}

        # Recursive instantiation
        top_node = Node(gate.id_, event_from_id, gate_from_id, parent_node=None)

        # Recursive sizing and positioning
        top_node.determine_size_recursive()
        top_node.determine_position_recursive()

        # Finalisation
        self.top_node = top_node

    def __repr__(self):
        return natural_repr(self)


class Node:
    """
    Class representing a node (event or gate) within a figure.

    Nodes are instantiated recursively, starting from the top node of the figure.
    """
    def __init__(self, id_: str, event_from_id: dict[str, 'Event'], gate_from_id: dict[str, 'Gate'],
                 parent_node: Optional['Node']):
        if id_ in event_from_id:
            source_object = event_from_id[id_]
            input_nodes = []

        elif id_ in gate_from_id:
            source_object = gate = gate_from_id[id_]

            if gate.is_paged and parent_node is not None:
                input_nodes = []
            else:
                input_nodes = [
                    Node(input_id, event_from_id, gate_from_id, parent_node=self)
                    for input_id in gate.input_ids
                ]

        else:
            raise ImplementationError(f'bad id_ {id_}')

        # Indirect fields (from parameters)
        self.source_object = source_object
        self.input_nodes = input_nodes
        self.parent_node = parent_node

        # Fields to be set by figure
        self.bounding_width = None
        self.bounding_height = None
        self.x = None
        self.y = None


    def __str__(self):
        head = f'Node({self.source_object.id_})'
        sequence = ', '.join(str(node) for node in self.input_nodes)
        delimited_sequence = f'<{sequence}>' if sequence else ''

        return head + delimited_sequence

    def determine_size_recursive(self) -> tuple[int, int]:
        """
        Determine node size recursively (contributions propagated bottom-up).
        """
        if not self.input_nodes:
            self.bounding_width = EVENT_BOUNDING_WIDTH
            self.bounding_height = EVENT_BOUNDING_HEIGHT
        else:
            input_node_sizes = [node.determine_size_recursive() for node in self.input_nodes]
            input_widths, input_heights = zip(*input_node_sizes)

            self.bounding_width = sum(input_widths)
            self.bounding_height = EVENT_BOUNDING_HEIGHT + max(input_heights)

        return self.bounding_width, self.bounding_height

    def determine_position_recursive(self):
        """
        Determine node position recursively (propagated top-down).
        """
        parent_node = self.parent_node

        if parent_node is None:
            self.x = self.bounding_width // 2
            self.y = self.bounding_height // 2
        else:
            parent_inputs = parent_node.input_nodes
            sibling_index = parent_inputs.index(self)
            siblings_before = parent_inputs[0:sibling_index]
            width_before = sum(node.bounding_width for node in siblings_before)

            self.x = parent_node.x - parent_node.bounding_width // 2 + width_before + self.bounding_width // 2
            self.y = parent_node.y + EVENT_BOUNDING_HEIGHT

        for input_node in self.input_nodes:
            input_node.determine_position_recursive()


class Table:
    """
    Class representing tabular output.
    """
    def __init__(self, headings: list[str], data: list[list]):
        self.headings = headings
        self.data = data

    def __repr__(self):
        return natural_repr(self)

    def write_tsv(self, file_name: str):
        with open(file_name, 'w', encoding='utf-8', newline='') as file:
            writer = csv.writer(file, delimiter='\t', lineterminator=os.linesep)
            writer.writerow(self.headings)
            writer.writerows(self.data)
