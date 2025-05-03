"""
# Public Fault Tree Analyser: graphics.py

Graphical classes representing SVG content.

**Copyright 2025 Conway.**
Licensed under the GNU General Public License v3.0 (GPL-3.0-only).
This is free software with NO WARRANTY etc. etc., see LICENSE.
"""
import string
from typing import TYPE_CHECKING, Union

from pfta.constants import GateType, SymbolType
from pfta.woe import ImplementationError

if TYPE_CHECKING:
    from pfta.core import Event, Gate
    from pfta.presentation import Node


PAGE_MARGIN = 10
DEFAULT_FONT_SIZE = 10

EVENT_BOUNDING_WIDTH = 120
EVENT_BOUNDING_HEIGHT = 210

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

PAGED_GATE_APEX_HEIGHT = 36  # tip, above centre
PAGED_GATE_BODY_HEIGHT = 32  # toes, below centre
PAGED_GATE_HALF_WIDTH = 40

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


class SymbolGraphic(Graphic):
    x: int
    y: int
    type_: SymbolType

    def __init__(self, node: 'Node'):
        self.x = node.x
        self.y = node.y
        self.type_ = SymbolGraphic.determine_type(node.source_object)

    def svg_content(self) -> str:
        if self.type_ == SymbolType.OR_GATE:
            return SymbolGraphic.or_gate_svg_content(self.x, self.y)

        if self.type_ == SymbolType.AND_GATE:
            return SymbolGraphic.and_gate_svg_content(self.x, self.y)

        if self.type_ == SymbolType.PAGED_GATE:
            return SymbolGraphic.paged_gate_svg_content(self.x, self.y)

        if self.type_ in (SymbolType.DEVELOPED_EVENT, SymbolType.UNDEVELOPED_EVENT):  # TODO: separate undeveloped
            return 'EVENT'  # TODO: implement properly

        raise ImplementationError(f'bad symbol type {self.type_}')

    @staticmethod
    def determine_type(source_object: Union['Event', 'Gate']) -> SymbolType:
        class_name = type(source_object).__name__

        if class_name == 'Event':
            event = source_object

            if event.actual_model_type == 'Undeveloped':
                return SymbolType.UNDEVELOPED_EVENT
            else:
                return SymbolType.DEVELOPED_EVENT

        if class_name == 'Gate':
            gate = source_object

            if gate.is_paged:
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


def figure_svg_content(bounding_width: int, bounding_height: int, graphics: list[Graphic]) -> str:
    left = -PAGE_MARGIN
    top = -PAGE_MARGIN
    width = bounding_width + 2 * PAGE_MARGIN
    height = bounding_height + 2 * PAGE_MARGIN

    font_size = DEFAULT_FONT_SIZE
    body_content = '\n'.join(graphic.svg_content() for graphic in graphics)

    return FIGURE_SVG_TEMPLATE.substitute({
        'left': left, 'top': top, 'width': width, 'height': height,
        'font_size': font_size, 'body_content': body_content,
    })
