"""
# Public Fault Tree Analyser: presentation.py

Presentational classes.

**Copyright 2025 Conway.**
Licensed under the GNU General Public License v3.0 (GPL-3.0-only).
This is free software with NO WARRANTY etc. etc., see LICENSE.
"""

import csv
import os
from typing import TYPE_CHECKING

from pfta.common import natural_repr
from pfta.woe import ImplementationError

if TYPE_CHECKING:
    from pfta.core import FaultTree, Event, Gate


class Figure:
    """
    Class representing a figure (a page of a fault tree).
    """
    def __init__(self, gate: 'Gate', fault_tree: 'FaultTree'):
        event_from_id = {event.id_: event for event in fault_tree.events}
        gate_from_id = {gate.id_: gate for gate in fault_tree.gates}

        # Recursive instantiation
        top_node = Node(gate.id_, event_from_id, gate_from_id, is_top_node=True)

        # Recursive sizing and positioning
        # TODO

        # Finalisation
        self.top_node = top_node

    def __repr__(self):
        return natural_repr(self)


class Node:
    """
    Class representing a node (event or gate) within a figure.

    Nodes are instantiated recursively, starting from the top node of the figure.
    """
    def __init__(self, id_: str, event_from_id: dict[str, 'Event'], gate_from_id: dict[str, 'Gate'], is_top_node: bool):
        if id_ in event_from_id:
            source_object = event_from_id[id_]
            input_nodes = []

        elif id_ in gate_from_id:
            source_object = gate = gate_from_id[id_]

            if gate.is_paged and not is_top_node:
                input_nodes = []
            else:
                input_nodes = [
                    Node(input_id, event_from_id, gate_from_id, is_top_node=False)
                    for input_id in gate.input_ids
                ]

        else:
            raise ImplementationError(f'bad id_ {id_}')

        # Indirect fields (from parameters)
        self.source_object = source_object
        self.input_nodes = input_nodes

        # Fields to be set by figure
        # TODO

    def __str__(self):
        head = f'Node({self.source_object.id_})'
        sequence = ', '.join(str(node) for node in self.input_nodes)
        delimited_sequence = f'<{sequence}>' if sequence else ''

        return head + delimited_sequence


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
