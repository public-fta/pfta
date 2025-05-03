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

FIGURE_SVG_TEMPLATE = string.Template('''\
<?xml version="1.0" encoding="UTF-8"?>
<svg viewBox="${left} ${top} ${width} ${height}" xmlns="http://www.w3.org/2000/svg">
<style>
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
        self.type_ = event_symbol_type(node.source_object)

    def svg_content(self) -> str:
        return f'<text x="{self.x}" y="{self.y}">{self.type_}</text>'  # TODO: implement properly


def event_symbol_type(source_object: Union['Event', 'Gate']) -> SymbolType:
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
