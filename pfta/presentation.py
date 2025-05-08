"""
# Public Fault Tree Analyser: presentation.py

Presentational classes.

**Copyright 2025 Conway.**
Licensed under the GNU General Public License v3.0 (GPL-3.0-only).
This is free software with NO WARRANTY etc. etc., see LICENSE.
"""

import collections
import csv
import os
import string
from typing import TYPE_CHECKING, Optional, Union

from pfta.common import natural_repr, format_quantity
from pfta.graphics import (
    EVENT_BOUNDING_WIDTH, EVENT_BOUNDING_HEIGHT,
    Graphic, TimeHeaderGraphic, LabelConnectorGraphic, InputConnectorsGraphic,
    LabelBoxGraphic, LabelTextGraphic, IdentifierBoxGraphic, IdentifierTextGraphic,
    SymbolGraphic, QuantityBoxGraphic, QuantityTextGraphic,
    figure_svg_content, escape_xml,
)
from pfta.woe import ImplementationError

if TYPE_CHECKING:
    from pfta.core import FaultTree, Event, Gate


INDEX_HTML_TEMPLATE = string.Template('''\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Index of `${figures_directory_name}`</title>
  <style>
    html {
      margin: 0 auto;
      max-width: 45em;
    }
    table {
      border-spacing: 0;
      border-collapse: collapse;
      margin-top: 0.5em;
      margin-bottom: 1em;
    }
    th {
      background-clip: padding-box;
      background-color: lightgrey;
      position: sticky;
      top: 0;
    }
    th, td {
      border: 1px solid black;
      padding: 0.4em;
    }
  </style>
</head>
<body>
<h1>Index of <code>${figures_directory_name}</code></h1>
<h2>Lookup by object</h2>
<table>
  <thead>
    <tr>
      <th>Object</th>
      <th>Label</th>
      <th>Figures by ${scaled_time_variable_content}</th>
    </tr>
  </thead>
  <tbody>
${object_lookup_content}
  </tbody>
</table>
<h2>Lookup by figure</h2>
<table>
  <thead>
    <tr>
      <th>Figure by ${scaled_time_variable_content}</th>
      <th>Label</th>
      <th>Objects</th>
    </tr>
  </thead>
  <tbody>
${figure_lookup_content}
  </tbody>
</table>
</body>
</html>
''')


class Figure:
    """
    Class representing a figure (a page of a fault tree).
    """
    id_: str
    label: str
    top_node: 'Node'
    graphics: list[Graphic]

    def __init__(self, time_index: int, gate: 'Gate', fault_tree: 'FaultTree'):
        event_from_id = {event.id_: event for event in fault_tree.events}
        gate_from_id = {gate.id_: gate for gate in fault_tree.gates}

        # Recursive instantiation
        top_node = Node(gate.id_, time_index, fault_tree, event_from_id, gate_from_id, parent_node=None)

        # Recursive sizing and positioning
        top_node.determine_reachables_recursive()
        top_node.determine_size_recursive()
        top_node.determine_position_recursive()

        # Graphics assembly
        time_header_graphic = TimeHeaderGraphic(time_index, fault_tree, top_node.bounding_width)
        node_graphics = [
            graphic for node in top_node.reachable_nodes
            for graphic in node.assemble_graphics()
        ]

        # Finalisation
        self.id_ = top_node.source_object.id_
        self.label = top_node.source_object.label
        self.top_node = top_node
        self.graphics = [time_header_graphic, *node_graphics]

    def __lt__(self, other):
        return self.id_ < other.id_

    def __repr__(self):
        return natural_repr(self)

    def svg_content(self) -> str:
        bounding_width = self.top_node.bounding_width
        bounding_height = self.top_node.bounding_height
        graphics = self.graphics

        return figure_svg_content(bounding_width, bounding_height, graphics)

    def write_svg(self, file_name: str):
        with open(file_name, 'w', encoding='utf-8', newline='') as file:
            file.write(self.svg_content())


class Node:
    """
    Class representing a node (event or gate) within a figure.

    Nodes are instantiated recursively, starting from the top node of the figure.
    """
    fault_tree: 'FaultTree'
    source_object: Union['Event', 'Gate']
    input_nodes: list['Node']
    parent_node: 'Node'

    reachable_nodes: Optional[list['Node']]
    bounding_width: Optional[int]
    bounding_height: Optional[int]
    x: Optional[int]
    y: Optional[int]

    def __init__(self, id_: str, time_index: int, fault_tree: 'FaultTree',
                 event_from_id: dict[str, 'Event'], gate_from_id: dict[str, 'Gate'], parent_node: Optional['Node']):
        if id_ in event_from_id:
            source_object = event_from_id[id_]
            input_nodes = []

        elif id_ in gate_from_id:
            source_object = gate = gate_from_id[id_]

            if gate.is_paged and parent_node is not None:
                input_nodes = []
            else:
                input_nodes = [
                    Node(input_id, time_index, fault_tree, event_from_id, gate_from_id, parent_node=self)
                    for input_id in gate.input_ids
                ]

        else:
            raise ImplementationError(f'bad id_ {id_}')

        # Indirect fields (from parameters)
        self.time_index = time_index
        self.fault_tree = fault_tree
        self.source_object = source_object
        self.input_nodes = input_nodes
        self.parent_node = parent_node

        # Fields to be set by figure
        self.reachable_nodes = None
        self.bounding_width = None
        self.bounding_height = None
        self.x = None
        self.y = None

    def __str__(self):
        head = f'Node({self.source_object.id_})'
        sequence = ', '.join(str(node) for node in self.input_nodes)
        delimited_sequence = f'<{sequence}>' if sequence else ''

        return head + delimited_sequence

    def determine_reachables_recursive(self) -> list['Node']:
        """
        Determine reachable nodes (self plus descendants) recursively (propagated bottom-up).
        """
        self.reachable_nodes = [
            self,
            *[
                reachable
                for input_node in self.input_nodes
                for reachable in input_node.determine_reachables_recursive()
            ],
        ]

        return self.reachable_nodes

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
            self.y = EVENT_BOUNDING_HEIGHT // 2
        else:
            parent_inputs = parent_node.input_nodes
            input_index = parent_inputs.index(self)
            siblings_before = parent_inputs[0:input_index]
            width_before = sum(node.bounding_width for node in siblings_before)

            self.x = parent_node.x - parent_node.bounding_width // 2 + width_before + self.bounding_width // 2
            self.y = parent_node.y + EVENT_BOUNDING_HEIGHT

        for input_node in self.input_nodes:
            input_node.determine_position_recursive()

    def assemble_graphics(self) -> list[Graphic]:
        return [
            LabelConnectorGraphic(self),
            InputConnectorsGraphic(self),
            LabelBoxGraphic(self),
            LabelTextGraphic(self),
            IdentifierBoxGraphic(self),
            IdentifierTextGraphic(self),
            SymbolGraphic(self),
            QuantityBoxGraphic(self),
            QuantityTextGraphic(self),
        ]


class Index:
    """
    Class representing an index of figures (tracing to and from their contained objects).
    """
    times: list[float]
    time_unit: str
    figures_from_object: dict[Union['Event', 'Gate'], set[Figure]]
    objects_from_figure: dict[Figure, set[Union['Event', 'Gate']]]
    figures_directory_name: str

    def __init__(self, figure_from_id_from_time: dict[float, dict[str, Figure]],
                 figures_directory_name: str, time_unit: str):
        times = list(figure_from_id_from_time.keys())
        figures = next(iter(figure_from_id_from_time.values())).values()

        figures_from_object = collections.defaultdict(set)
        objects_from_figure = collections.defaultdict(set)

        for figure in figures:
            for node in figure.top_node.reachable_nodes:
                figures_from_object[node.source_object].add(figure)
                objects_from_figure[figure].add(node.source_object)

        figures_from_object = dict(sorted(figures_from_object.items()))
        objects_from_figure = dict(sorted(objects_from_figure.items()))

        self.times = times
        self.time_unit = time_unit
        self.figures_from_object = figures_from_object
        self.objects_from_figure = objects_from_figure
        self.figures_directory_name = figures_directory_name

    def html_content(self) -> str:
        time_unit = self.time_unit
        figures_directory_name = self.figures_directory_name

        scaled_time_variable_content = format_quantity('<var>t</var>', time_unit, is_reciprocal=True)

        times = self.times
        object_lookup_content = '\n'.join(
            '\n'.join([
                f'    <tr>',
                f'      <td>{Index.object_content(object_)}</td>',
                f'      <td>{Index.label_content(object_.label)}</td>',
                f'      <td>{", ".join(Index.figure_content(figure, times) for figure in sorted(figures))}</td>',
                f'    </tr>',
            ])
            for object_, figures in self.figures_from_object.items()
        )
        figure_lookup_content = '\n'.join(
            '\n'.join([
                f'    <tr>',
                f'      <td>{Index.figure_content(figure, times)}</td>',
                f'      <td>{Index.label_content(figure.label)}</td>',
                f'      <td>{", ".join(Index.object_content(object_) for object_ in sorted(objects))}</td>',
                f'    </tr>',
            ])
            for figure, objects in self.objects_from_figure.items()
        )

        return INDEX_HTML_TEMPLATE.substitute({
            'figures_directory_name': figures_directory_name,
            'scaled_time_variable_content': scaled_time_variable_content,
            'object_lookup_content': object_lookup_content, 'figure_lookup_content': figure_lookup_content,
        })

    def write_html(self, file_name: str):
        with open(file_name, 'w', encoding='utf-8', newline='') as file:
            file.write(self.html_content())

    @staticmethod
    def object_content(source_object: Union['Event', 'Gate']) -> str:
        return f'<code>{escape_xml(source_object.id_)}</code>'

    @staticmethod
    def label_content(label: str) -> str:
        return escape_xml(label) if label else ''

    @staticmethod
    def figure_content(figure: Figure, times: list[float]) -> str:
        figure_id = figure.top_node.source_object.id_
        links_content = ', '.join(
            f'<a href="{escape_xml(str(time))}/{escape_xml(figure_id)}.svg"><code>{escape_xml(str(time))}</code></a>'
            for time in times
        )

        return f'<code>{escape_xml(figure_id)}.svg</code> ({links_content})'



class Table:
    """
    Class representing tabular output.
    """
    headings: list[str]
    data: list[list]

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
