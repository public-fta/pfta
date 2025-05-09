"""
# Public Fault Tree Analyser: graphics.py

Graphical classes representing SVG content.

**Copyright 2025 Conway.**
Licensed under the GNU General Public License v3.0 (GPL-3.0-only).
This is free software with NO WARRANTY etc. etc., see LICENSE.
"""

import html
import math
import re
import string
import textwrap
from typing import TYPE_CHECKING, Optional

import pfta.core
from pfta.boolean import Term, Expression
from pfta.common import format_quantity
from pfta.constants import EventAppearance, GateType, SymbolType
from pfta.utilities import format_number
from pfta.woe import ImplementationError

if TYPE_CHECKING:
    from pfta.core import FaultTree, Object
    from pfta.presentation import Node


PAGE_MARGIN = 10
DEFAULT_FONT_SIZE = 10
DEFAULT_LINE_SPACING = 1.3

TIME_HEADER_MARGIN = 20
TIME_HEADER_Y_OFFSET = -25
TIME_HEADER_FONT_SIZE = 16

EVENT_BOUNDING_WIDTH = 120
EVENT_BOUNDING_HEIGHT = 210

LABEL_BOX_Y_OFFSET = -65
LABEL_BOX_WIDTH = 108
LABEL_BOX_HEIGHT = 70
LABEL_BOX_TARGET_RATIO = 5.4  # line length divided by line count
LABEL_MIN_LINE_LENGTH = 16

IDENTIFIER_BOX_Y_OFFSET = -13
IDENTIFIER_BOX_WIDTH = 108
IDENTIFIER_BOX_HEIGHT = 24

SYMBOL_Y_OFFSET = 45
SYMBOL_SLOTS_HALF_WIDTH = 30

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

VOTE_GATE_THRESHOLD_TEXT_HEIGHT = 25  # number, above centre

PAGED_GATE_APEX_HEIGHT = 36  # tip, above centre
PAGED_GATE_BODY_HEIGHT = 32  # toes, below centre
PAGED_GATE_HALF_WIDTH = 40

BASIC_EVENT_RADIUS = 38

UNDEVELOPED_EVENT_HALF_HEIGHT = 38
UNDEVELOPED_EVENT_HALF_WIDTH = 54

HOUSE_EVENT_APEX_HEIGHT = 38  # tip, above centre
HOUSE_EVENT_SHOULDER_HEIGHT = 24  # corners, above centre
HOUSE_EVENT_BODY_HEIGHT = 26  # toes, below centre
HOUSE_EVENT_HALF_WIDTH = 36

QUANTITY_BOX_Y_OFFSET = 45
QUANTITY_BOX_WIDTH = 108
QUANTITY_BOX_HEIGHT = 32

INPUT_CONNECTOR_BUS_Y_OFFSET = 95
INPUT_CONNECTOR_BUS_HALF_HEIGHT = 10

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
  font-size: ${default_font_size}px;
  text-anchor: middle;
  white-space: pre;
}
.padding {
  user-select: none;
}
.time-header {
  font-size: ${time_header_font_size}px
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
    significant_figures: int
    scientific_exponent: int
    bounding_width: int

    def __init__(self, time_index: int, fault_tree: 'FaultTree', bounding_width: int):
        self.time = fault_tree.times[time_index]
        self.time_unit = fault_tree.time_unit
        self.significant_figures = fault_tree.significant_figures
        self.scientific_exponent = fault_tree.scientific_exponent
        self.bounding_width = bounding_width

    def svg_content(self) -> str:
        centre = self.bounding_width // 2
        middle = TIME_HEADER_Y_OFFSET

        time_value = format_number(self.time, significant_figures=self.significant_figures,
                                   scientific_exponent_threshold=self.scientific_exponent)
        time_quantity = format_quantity(time_value, self.time_unit)
        content = escape_xml(f't = {time_quantity}')

        return f'<text x="{centre}" y="{middle}" class="time-header">{content}</text>'


class LabelConnectorGraphic(Graphic):
    x: int
    y: int

    def __init__(self, node: 'Node'):
        self.x = node.x
        self.y = node.y

    def svg_content(self) -> str:
        centre = self.x
        label_middle = self.y + LABEL_BOX_Y_OFFSET
        symbol_middle = self.y + SYMBOL_Y_OFFSET

        points = f'{centre},{label_middle} {centre},{symbol_middle}'

        return f'<polyline points="{points}"/>'


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
        line_middle = format_number(middle + bias * font_size * DEFAULT_LINE_SPACING, decimal_places=1)
        content = escape_xml(line)

        return f'<text x="{centre}" y="{line_middle}" style="{style}">{content}</text>'


class IdentifierBoxGraphic(Graphic):
    x: int
    y: int

    def __init__(self, node: 'Node'):
        self.x = node.x
        self.y = node.y

    def svg_content(self) -> str:
        left = self.x - IDENTIFIER_BOX_WIDTH // 2
        top = self.y - IDENTIFIER_BOX_HEIGHT // 2 + IDENTIFIER_BOX_Y_OFFSET
        width = IDENTIFIER_BOX_WIDTH
        height = IDENTIFIER_BOX_HEIGHT

        return f'<rect x="{left}" y="{top}" width="{width}" height="{height}"/>'


class IdentifierTextGraphic(Graphic):
    x: int
    y: int
    id_: str

    def __init__(self, node: 'Node'):
        self.x = node.x
        self.y = node.y
        self.id_ = node.source_object.id_

    def svg_content(self) -> str:
        centre = self.x
        middle = self.y + IDENTIFIER_BOX_Y_OFFSET
        content = escape_xml(self.id_)

        return f'<text x="{centre}" y="{middle}">{content}</text>'


class SymbolGraphic(Graphic):
    x: int
    y: int
    type_: SymbolType
    vote_threshold: Optional[int]

    def __init__(self, node: 'Node'):
        self.x = node.x
        self.y = node.y
        self.type_ = SymbolGraphic.determine_type(node.parent_node, node.source_object)
        self.vote_threshold = SymbolGraphic.determine_vote_threshold(node.source_object)

    def svg_content(self) -> str:
        if self.type_ == SymbolType.OR_GATE:
            return SymbolGraphic.or_gate_svg_content(self.x, self.y)

        if self.type_ == SymbolType.AND_GATE:
            return SymbolGraphic.and_gate_svg_content(self.x, self.y)

        if self.type_ == SymbolType.VOTE_GATE:
            return SymbolGraphic.vote_gate_svg_content(self.x, self.y, self.vote_threshold)

        if self.type_ == SymbolType.PAGED_GATE:
            return SymbolGraphic.paged_gate_svg_content(self.x, self.y)

        if self.type_ == SymbolType.NULL_GATE:
            return ''

        if self.type_ == SymbolType.BASIC_EVENT:
            return SymbolGraphic.basic_event_svg_content(self.x, self.y)

        if self.type_ == SymbolType.UNDEVELOPED_EVENT:
            return SymbolGraphic.undeveloped_event_svg_content(self.x, self.y)

        if self.type_ == SymbolType.HOUSE_EVENT:
            return SymbolGraphic.house_event_svg_content(self.x, self.y)

        raise ImplementationError(f'bad symbol type {self.type_}')

    @staticmethod
    def determine_type(parent_node: Optional['Node'], source_object: 'Object') -> SymbolType:
        if isinstance(source_object, pfta.core.Event):
            event = source_object

            if event.appearance == EventAppearance.BASIC:
                return SymbolType.BASIC_EVENT

            if event.appearance == EventAppearance.UNDEVELOPED:
                return SymbolType.UNDEVELOPED_EVENT

            if event.appearance == EventAppearance.HOUSE:
                return SymbolType.HOUSE_EVENT

            raise ImplementationError(f'bad event appearance {event.appearance}')

        if isinstance(source_object, pfta.core.Gate):
            gate = source_object

            if gate.is_paged and parent_node is not None:
                return SymbolType.PAGED_GATE

            if len(gate.input_ids) == 1:
                return SymbolType.NULL_GATE

            if gate.type_ == GateType.OR:
                return SymbolType.OR_GATE

            if gate.type_ == GateType.AND:
                return SymbolType.AND_GATE

            if gate.type_ == GateType.VOTE:
                return SymbolType.VOTE_GATE

            raise ImplementationError(f'bad gate type {gate.type_}')

        raise ImplementationError(f'bad class_name {type(source_object).__name__}')

    @staticmethod
    def determine_vote_threshold(source_object: 'Object') -> Optional[int]:
        if isinstance(source_object, pfta.core.Gate):
            return source_object.vote_threshold

        return None

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
    def vote_gate_svg_content(x: int, y: int, vote_threshold: Optional[int]) -> str:
        text_x = x
        text_y = y - VOTE_GATE_THRESHOLD_TEXT_HEIGHT + SYMBOL_Y_OFFSET
        content = vote_threshold

        return '\n'.join([
            SymbolGraphic.or_gate_svg_content(x, y),
            f'<text x="{text_x}" y="{text_y}">{content}</text>'
        ])

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
    def basic_event_svg_content(x: int, y: int) -> str:
        centre = x
        middle = y + SYMBOL_Y_OFFSET
        radius = BASIC_EVENT_RADIUS

        return f'<circle cx="{centre}" cy="{middle}" r="{radius}"/>'

    @staticmethod
    def undeveloped_event_svg_content(x: int, y: int) -> str:
        top_x = bottom_x = x
        left_y = right_y = y + SYMBOL_Y_OFFSET

        left_x = x - UNDEVELOPED_EVENT_HALF_WIDTH
        right_x = x + UNDEVELOPED_EVENT_HALF_WIDTH
        top_y = y - UNDEVELOPED_EVENT_HALF_HEIGHT + SYMBOL_Y_OFFSET
        bottom_y = y + UNDEVELOPED_EVENT_HALF_HEIGHT + SYMBOL_Y_OFFSET

        points = f'{top_x},{top_y} {left_x},{left_y} {bottom_x},{bottom_y} {right_x},{right_y}'

        return f'<polygon points="{points}"/>'

    @staticmethod
    def house_event_svg_content(x: int, y: int) -> str:
        top_x = x
        top_y = y - HOUSE_EVENT_APEX_HEIGHT + SYMBOL_Y_OFFSET

        left_x = x - HOUSE_EVENT_HALF_WIDTH
        right_x = x + HOUSE_EVENT_HALF_WIDTH
        shoulder_y = y - HOUSE_EVENT_SHOULDER_HEIGHT + SYMBOL_Y_OFFSET
        toe_y = y + HOUSE_EVENT_BODY_HEIGHT + SYMBOL_Y_OFFSET

        points = f'{top_x},{top_y} {left_x},{shoulder_y} {left_x},{toe_y} {right_x},{toe_y} {right_x},{shoulder_y}'

        return f'<polygon points="{points}"/>'


class QuantityBoxGraphic(Graphic):
    x: int
    y: int

    def __init__(self, node: 'Node'):
        self.x = node.x
        self.y = node.y

    def svg_content(self) -> str:
        left = self.x - QUANTITY_BOX_WIDTH // 2
        top = self.y - QUANTITY_BOX_HEIGHT // 2 + QUANTITY_BOX_Y_OFFSET
        width = QUANTITY_BOX_WIDTH
        height = QUANTITY_BOX_HEIGHT

        return f'<rect x="{left}" y="{top}" width="{width}" height="{height}"/>'


class QuantityTextGraphic(Graphic):
    x: int
    y: int
    expression: Expression
    probability: float
    intensity: float
    sample_size: int
    time_unit: str
    significant_figures: int
    scientific_exponent: int

    def __init__(self, node: 'Node'):
        self.x = node.x
        self.y = node.y
        self.expression = node.source_object.computed_expression
        self.probability = node.source_object.computed_expected_probabilities[node.time_index]
        self.intensity = node.source_object.computed_expected_intensities[node.time_index]
        self.sample_size = node.fault_tree.sample_size
        self.time_unit = node.fault_tree.time_unit
        self.significant_figures = node.fault_tree.significant_figures
        self.scientific_exponent = node.fault_tree.scientific_exponent

    def svg_content(self) -> str:
        centre = self.x
        middle = self.y + QUANTITY_BOX_Y_OFFSET

        if self.expression == Expression(Term(encoding=0)):
            return f'<text x="{centre}" y="{middle}">True</text>'

        if self.expression == Expression():
            return f'<text x="{centre}" y="{middle}">False</text>'

        line_half_gap = DEFAULT_FONT_SIZE * DEFAULT_LINE_SPACING / 2
        probability_middle = format_number(middle - line_half_gap, decimal_places=1)
        intensity_middle = format_number(middle + line_half_gap, decimal_places=1)

        probability_value = format_number(self.probability, significant_figures=self.significant_figures,
                                          scientific_exponent_threshold=self.scientific_exponent)
        probability_rhs = escape_xml(probability_value)

        intensity_value = format_number(self.intensity, significant_figures=self.significant_figures,
                                        scientific_exponent_threshold=self.scientific_exponent)
        intensity_quantity = format_quantity(intensity_value, self.time_unit, is_reciprocal=True)
        intensity_rhs = escape_xml(intensity_quantity)

        max_rhs_length = max(
            probability_rhs_length := len(unescape_xml(probability_rhs)),
            intensity_rhs_length := len(unescape_xml(intensity_rhs)),
        )
        probability_spaces = (max_rhs_length - probability_rhs_length) * ' '
        intensity_spaces = (max_rhs_length - intensity_rhs_length) * ' '
        probability_padding = f'<tspan class="padding">{probability_spaces}</tspan>' if probability_spaces else ''
        intensity_padding = f'<tspan class="padding">{intensity_spaces}</tspan>' if intensity_spaces else ''

        probability_content = f'q = {probability_rhs}' + probability_padding
        intensity_content = f'ω = {intensity_rhs}' + intensity_padding

        if self.sample_size > 1:
            tooltip = f'<title>mean value estimated from a sample of size {self.sample_size}</title>'
        else:
            tooltip = ''

        return '\n'.join([
            f'<text x="{centre}" y="{probability_middle}">{tooltip}{probability_content}</text>',
            f'<text x="{centre}" y="{intensity_middle}">{tooltip}{intensity_content}</text>',
        ])


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


def unescape_xml(xml: str) -> str:
    """
    Unescape XML entities.
    """
    return html.unescape(xml)


def figure_svg_content(bounding_width: int, bounding_height: int, graphics: list[Graphic]) -> str:
    left = -PAGE_MARGIN
    top = -PAGE_MARGIN - TIME_HEADER_MARGIN + TIME_HEADER_Y_OFFSET
    width = bounding_width + 2 * PAGE_MARGIN
    height = bounding_height + TIME_HEADER_MARGIN - TIME_HEADER_Y_OFFSET + 2 * PAGE_MARGIN

    default_font_size = DEFAULT_FONT_SIZE
    time_header_font_size = TIME_HEADER_FONT_SIZE
    body_content = '\n'.join(
        svg_content
        for graphic in graphics
        if (svg_content := graphic.svg_content())
    )

    return FIGURE_SVG_TEMPLATE.substitute({
        'left': left, 'top': top, 'width': width, 'height': height,
        'default_font_size': default_font_size, 'time_header_font_size': time_header_font_size,
        'body_content': body_content,
    })
