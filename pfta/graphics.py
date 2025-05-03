"""
# Public Fault Tree Analyser: graphics.py

Graphical classes representing SVG content.

**Copyright 2025 Conway.**
Licensed under the GNU General Public License v3.0 (GPL-3.0-only).
This is free software with NO WARRANTY etc. etc., see LICENSE.
"""

from typing import TYPE_CHECKING, Union

from pfta.constants import GateType, SymbolType
from pfta.woe import ImplementationError

if TYPE_CHECKING:
    from pfta.core import Event, Gate
    from pfta.presentation import Node


EVENT_BOUNDING_WIDTH = 120
EVENT_BOUNDING_HEIGHT = 210


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
