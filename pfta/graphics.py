"""
# Public Fault Tree Analyser: graphics.py

Graphical classes representing SVG content.

**Copyright 2025 Conway.**
Licensed under the GNU General Public License v3.0 (GPL-3.0-only).
This is free software with NO WARRANTY etc. etc., see LICENSE.
"""

import math
import re
import string
import textwrap
from typing import TYPE_CHECKING, Optional, Union

from pfta.constants import GateType, SymbolType
from pfta.utilities import format_number
from pfta.woe import ImplementationError

if TYPE_CHECKING:
    from pfta.core import Event, Gate
    from pfta.presentation import Node


PAGE_MARGIN = 10
DEFAULT_FONT_SIZE = 10
LINE_SPACING = 1.3

TIME_HEADER_MARGIN = 20
TIME_HEADER_Y_OFFSET = 25
TIME_HEADER_FONT_SIZE = 16

EVENT_BOUNDING_WIDTH = 120
EVENT_BOUNDING_HEIGHT = 210

SYMBOL_Y_OFFSET = 45
SYMBOL_SLOTS_HALF_WIDTH = 30

LABEL_BOX_Y_OFFSET = -65
LABEL_BOX_WIDTH = 108
LABEL_BOX_HEIGHT = 70
LABEL_BOX_TARGET_RATIO = 5.4  # line length divided by line count
LABEL_MIN_LINE_LENGTH = 16

INPUT_CONNECTOR_BUS_Y_OFFSET = 95
INPUT_CONNECTOR_BUS_HALF_HEIGHT = 10

OR_GATE_APEX_HEIGHT = 38  # tip, above centre
OR_GATE_NECK_HEIGHT = -10  # ears, above centre
OR_GATE_BODY_HEIGHT = 36  # toes, below centre
OR_GATE_SLANT_DROP = 2  # control points, below apex
OR_GATE_SLANT_RUN = 6  # control points, beside apex
OR_GATE_SLING_RISE = 35  # control points, above toes
OR_GATE_GROIN_RISE = 30  # control point, between toes
OR_GATE_HALF_WIDTH = 33

AND_GATE_NECK_HEIGHT = 6  # ears, above centre
AND_GATE_BODY_HEIGHT = 34  # toes, below centre
AND_GATE_SLING_RISE = 42  # control points, above toes
AND_GATE_HALF_WIDTH = 32

PAGED_GATE_APEX_HEIGHT = 36  # tip, above centre
PAGED_GATE_BODY_HEIGHT = 32  # toes, below centre
PAGED_GATE_HALF_WIDTH = 40

DEVELOPED_EVENT_CIRCLE_RADIUS = 30
UNDEVELOPED_EVENT_CIRCUMRADIUS = 35

FIGURE_SVG_TEMPLATE = string.Template('''\
<?xml version="1.0" encoding="UTF-8"?>
<svg viewBox="${left} ${top} ${width} ${height}" xmlns="http://www.w3.org/2000/svg">
<style>
circle, path, polygon, rect {
  fill: lightyellow;
}
circle, path, polygon, polyline, rect {
  stroke: black;
  stroke-width: 1.3;
}
polyline {
  fill: none;
}
text {
  dominant-baseline: middle;
  font-family: Consolas, Cousine, "Courier New", monospace;
  font-size: ${font_size}px;
  text-anchor: middle;
}
</style>
${body_content}
</svg>
''')


class Graphic:
    def svg_content(self) -> str:
        raise NotImplementedError


class TimeHeaderGraphic(Graphic):
    time: float
    time_unit: str
    bounding_width: int

    def __init__(self, time: float, time_unit: str, significant_figures: int, bounding_width: int):
        self.time = time
        self.time_unit = time_unit
        self.significant_figures = significant_figures
        self.bounding_width = bounding_width

    def svg_content(self) -> str:
        centre = self.bounding_width // 2
        middle = -TIME_HEADER_Y_OFFSET
        style = f'font-size: {TIME_HEADER_FONT_SIZE}px'

        time_value = format_number(self.time, significant_figures=self.significant_figures)
        content = f't = {time_value} {self.time_unit}'  # TODO: robust unit formatting

        return f'<text x="{centre}" y="{middle}" style="{style}">{content}</text>'


class InputConnectorsGraphic(Graphic):
    x: int
    y: int
    input_nodes: list['Node']

    def __init__(self, node: 'Node'):
        self.x = node.x
        self.y = node.y
        self.input_nodes = node.input_nodes

    def svg_content(self) -> str:
        if not (input_nodes := self.input_nodes):
            return ''

        symbol_centre = self.x
        symbol_middle = self.y + SYMBOL_Y_OFFSET
        bus_middle = self.y + INPUT_CONNECTOR_BUS_Y_OFFSET

        input_count = len(input_nodes)
        slot_biases = [2 * n / (1 + input_count) - 1 for n in range(1, input_count + 1)]

        left_count, right_count, centre_count = InputConnectorsGraphic.input_partition_sizes(input_nodes, symbol_centre)
        bus_biases = [
            *[2 * n / (1 + left_count) - 1 for n in range(1, left_count + 1)],
            *[0 for _ in range(centre_count)],
            *[1 - 2 * n / (1 + right_count) for n in range(1, right_count + 1)],
        ]

        connector_coordinates_by_input = [
            InputConnectorsGraphic.connector_coordinates(
                input_node, slot_bias, bus_bias,
                symbol_centre, symbol_middle, bus_middle,
            )
            for input_node, slot_bias, bus_bias in zip(input_nodes, slot_biases, bus_biases)
        ]

        return '\n'.join(
            f'<polyline points="{InputConnectorsGraphic.points_svg_content(coordinates)}"/>'
            for coordinates in connector_coordinates_by_input
        )

    @staticmethod
    def input_partition_sizes(input_nodes: list['Node'], symbol_centre: int) -> tuple[int, int, int]:
        left_count = 0
        right_count = 0
        centre_count = 0

        for input_node in input_nodes:
            if input_node.x < symbol_centre:
                left_count += 1
            elif input_node.x > symbol_centre:
                right_count += 1
            else:
                centre_count += 1

        return left_count, right_count, centre_count

    @staticmethod
    def connector_coordinates(input_node: 'Node', slot_bias: float, bus_bias: float,
                              symbol_centre: int, symbol_middle: int, bus_middle: int) -> list[tuple[int, int]]:
        slot_x = round(symbol_centre + slot_bias * SYMBOL_SLOTS_HALF_WIDTH)
        bus_y = round(bus_middle + bus_bias * INPUT_CONNECTOR_BUS_HALF_HEIGHT)
        input_label_centre = input_node.x
        input_label_middle = input_node.y + LABEL_BOX_Y_OFFSET

        return [
            (slot_x, symbol_middle),
            (slot_x, bus_y),
            (input_label_centre, bus_y),
            (input_label_centre, input_label_middle),
        ]

    @staticmethod
    def points_svg_content(coordinates: list[tuple[int, int]]) -> str:
        return ' '.join(f'{x},{y}' for x, y in coordinates)


class LabelBoxGraphic(Graphic):
    x: int
    y: int

    def __init__(self, node: 'Node'):
        self.x = node.x
        self.y = node.y

    def svg_content(self) -> str:
        left = self.x - LABEL_BOX_WIDTH // 2
        top = self.y - LABEL_BOX_HEIGHT // 2 + LABEL_BOX_Y_OFFSET
        width = LABEL_BOX_WIDTH
        height = LABEL_BOX_HEIGHT

        return f'<rect x="{left}" y="{top}" width="{width}" height="{height}"/>'


class LabelTextGraphic(Graphic):
    x: int
    y: int
    label: str

    def __init__(self, node: 'Node'):
        self.x = node.x
        self.y = node.y
        self.label = node.source_object.label

    def svg_content(self) -> str:
        if not self.label:
            return ''

        centre = self.x
        middle = self.y + LABEL_BOX_Y_OFFSET

        ratio_based_line_length = round(math.sqrt(LABEL_BOX_TARGET_RATIO * len(self.label)))
        target_line_length = max(LABEL_MIN_LINE_LENGTH, ratio_based_line_length)
        lines = textwrap.wrap(self.label, target_line_length)
        line_count = len(lines)

        max_line_length = max((len(line) for line in lines), default=1)
        font_scale_factor = min(1., LABEL_MIN_LINE_LENGTH / max_line_length)
        font_size = round(font_scale_factor * DEFAULT_FONT_SIZE)
        style = f'font-size: {font_size}px'

        return '\n'.join(
            LabelTextGraphic.line_svg_content(line_number, line, centre, middle, line_count, font_size, style)
            for line_number, line in enumerate(lines, start=1)
        )

    @staticmethod
    def line_svg_content(line_number: int, line: str, centre: int, middle: int, line_count: int,
                         font_size: int, style: str) -> str:
        bias = line_number - (1 + line_count) / 2
        line_middle = format_number(middle + bias * font_size * LINE_SPACING, decimal_places=1)
        content = escape_xml(line)

        return f'<text x="{centre}" y="{line_middle}" style="{style}">{content}</text>'


class SymbolGraphic(Graphic):
    x: int
    y: int
    type_: SymbolType

    def __init__(self, node: 'Node'):
        self.x = node.x
        self.y = node.y
        self.type_ = SymbolGraphic.determine_type(node.parent_node, node.source_object)

    def svg_content(self) -> str:
        if self.type_ == SymbolType.OR_GATE:
            return SymbolGraphic.or_gate_svg_content(self.x, self.y)

        if self.type_ == SymbolType.AND_GATE:
            return SymbolGraphic.and_gate_svg_content(self.x, self.y)

        if self.type_ == SymbolType.PAGED_GATE:
            return SymbolGraphic.paged_gate_svg_content(self.x, self.y)

        if self.type_ == SymbolType.DEVELOPED_EVENT:
            return SymbolGraphic.developed_event_svg_content(self.x, self.y)

        if self.type_ == SymbolType.UNDEVELOPED_EVENT:
            return SymbolGraphic.undeveloped_event_svg_content(self.x, self.y)

        raise ImplementationError(f'bad symbol type {self.type_}')

    @staticmethod
    def determine_type(parent_node: Optional['Node'], source_object: Union['Event', 'Gate']) -> SymbolType:
        class_name = type(source_object).__name__

        if class_name == 'Event':
            event = source_object

            if event.actual_model_type == 'Undeveloped':
                return SymbolType.UNDEVELOPED_EVENT
            else:
                return SymbolType.DEVELOPED_EVENT

        if class_name == 'Gate':
            gate = source_object

            if gate.is_paged and parent_node is not None:
                return SymbolType.PAGED_GATE

            if gate.type_ == GateType.OR:
                return SymbolType.OR_GATE

            if gate.type_ == GateType.AND:
                return SymbolType.AND_GATE

            raise ImplementationError(f'bad gate type {gate.type_}')

        raise ImplementationError(f'bad class_name {class_name}')

    @staticmethod
    def or_gate_svg_content(x: int, y: int) -> str:
        apex_x = x
        apex_y = y - OR_GATE_APEX_HEIGHT + SYMBOL_Y_OFFSET

        left_x = x - OR_GATE_HALF_WIDTH
        right_x = x + OR_GATE_HALF_WIDTH

        ear_y = y - OR_GATE_NECK_HEIGHT + SYMBOL_Y_OFFSET
        toe_y = y + OR_GATE_BODY_HEIGHT + SYMBOL_Y_OFFSET

        left_slant_x = apex_x - OR_GATE_SLANT_RUN
        right_slant_x = apex_x + OR_GATE_SLANT_RUN
        slant_y = apex_y + OR_GATE_SLANT_DROP

        sling_y = ear_y - OR_GATE_SLING_RISE

        groin_x = x
        groin_y = toe_y - OR_GATE_GROIN_RISE

        commands = ' '.join([
            f'M{apex_x},{apex_y}',
            f'C{left_slant_x},{slant_y} {left_x},{sling_y} {left_x},{ear_y}',
            f'L{left_x},{toe_y}',
            f'Q{groin_x},{groin_y} {right_x},{toe_y}',
            f'L{right_x},{ear_y}',
            f'C{right_x},{sling_y} {right_slant_x},{slant_y} {apex_x},{apex_y}',
        ])

        return f'<path d="{commands}"/>'

    @staticmethod
    def and_gate_svg_content(x: int, y: int) -> str:
        left_x = x - AND_GATE_HALF_WIDTH
        right_x = x + AND_GATE_HALF_WIDTH

        ear_y = y - AND_GATE_NECK_HEIGHT + SYMBOL_Y_OFFSET
        toe_y = y + AND_GATE_BODY_HEIGHT + SYMBOL_Y_OFFSET

        sling_y = ear_y - AND_GATE_SLING_RISE

        commands = ' '.join([
            f'M{left_x},{toe_y}',
            f'L{right_x},{toe_y}',
            f'L{right_x},{ear_y}',
            f'C{right_x},{sling_y} {left_x},{sling_y} {left_x},{ear_y}',
            f'L{left_x},{toe_y}',
        ])

        return f'<path d="{commands}"/>'

    @staticmethod
    def paged_gate_svg_content(x: int, y: int) -> str:
        apex_x = x
        apex_y = y - PAGED_GATE_APEX_HEIGHT + SYMBOL_Y_OFFSET

        left_x = x - PAGED_GATE_HALF_WIDTH
        right_x = x + PAGED_GATE_HALF_WIDTH
        toe_y = y + PAGED_GATE_BODY_HEIGHT + SYMBOL_Y_OFFSET

        points = f'{apex_x},{apex_y} {left_x},{toe_y} {right_x},{toe_y}'

        return f'<polygon points="{points}"/>'

    @staticmethod
    def developed_event_svg_content(x: int, y: int) -> str:
        centre = x
        middle = y + SYMBOL_Y_OFFSET
        radius = DEVELOPED_EVENT_CIRCLE_RADIUS

        return f'<circle cx="{centre}" cy="{middle}" r="{radius}"/>'

    @staticmethod
    def undeveloped_event_svg_content(x: int, y: int) -> str:
        centre = x
        middle = y + SYMBOL_Y_OFFSET
        circumradius = UNDEVELOPED_EVENT_CIRCUMRADIUS

        top_x = bottom_x = centre
        left_y = right_y = middle

        left_x = centre - circumradius
        right_x = centre + circumradius
        top_y = middle - circumradius
        bottom_y = middle + circumradius

        points = f'{top_x},{top_y} {left_x},{left_y} {bottom_x},{bottom_y} {right_x},{right_y}'

        return f'<polygon points="{points}"/>'


def escape_xml(text: str) -> str:
    """
    Escape `&` (when not used in an entity), `<`, and `>`.
    """
    ampersand_pattern = re.compile(
        '''
            &
            (?!
                (?:
                    [a-z]{1,31}          # up to 31 letters in a name <https://html.spec.whatwg.org/entities.json>
                    | \# [0-9]{1,7}      # up to 7 decimal digits in a code point
                    | \# x[0-9a-f]{1,6}  # up to 6 hexadecimal digits in a code point
                )
                ;
            )
        ''',
        flags=re.IGNORECASE | re.VERBOSE,
    )

    text = re.sub(ampersand_pattern, '&amp;', text)
    text = re.sub('<', '&lt;', text)
    text = re.sub('>', '&gt;', text)

    return text


def figure_svg_content(bounding_width: int, bounding_height: int, graphics: list[Graphic]) -> str:
    left = -PAGE_MARGIN
    top = -PAGE_MARGIN - TIME_HEADER_MARGIN - TIME_HEADER_Y_OFFSET
    width = bounding_width + 2 * PAGE_MARGIN
    height = bounding_height + 2 * PAGE_MARGIN

    font_size = DEFAULT_FONT_SIZE
    body_content = '\n'.join(
        svg_content
        for graphic in graphics
        if (svg_content := graphic.svg_content())
    )

    return FIGURE_SVG_TEMPLATE.substitute({
        'left': left, 'top': top, 'width': width, 'height': height,
        'font_size': font_size, 'body_content': body_content,
    })
