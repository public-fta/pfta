"""
# Public Fault Tree Analyser: parsing.py

Parsing of fault tree text.

**Copyright 2025 Conway**
Licensed under the GNU General Public License v3.0 (GPL-3.0-only).
This is free software with NO WARRANTY etc. etc., see LICENSE.
"""

import re
from enum import Enum

from pfta.exceptions import FaultTreeTextException, ImplementationError


LINE_EXPLAINER = '\n'.join([
    'A line must have one of the following forms:',
    '    <class>: <identifier>  (an object declaration)',
    '    - <key>: <value>       (a property setting)',
    '    # <comment>            (a comment)',
    '    <blank line>           (used before the next declaration)',
])


class LineType(Enum):
    OBJECT = 0
    PROPERTY = 1
    COMMENT = 2
    BLANK = 3


class DanglingPropertyException(FaultTreeTextException):
    pass


class InvalidLineException(FaultTreeTextException):
    pass


class SmotheredObjectException(FaultTreeTextException):
    pass


class ParsedLine:
    def __init__(self, number: int, type_: LineType, content: str, info: dict):
        self.number = number
        self.type_ = type_
        self.content = content
        self.info = info

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class ParsedParagraph:
    def __init__(self, object_line: ParsedLine | None, property_lines: list[ParsedLine]):
        self.object_line = object_line
        self.property_lines = property_lines

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


def parse_line(line_number: int, line: str) -> ParsedLine:
    if object_match := re.match(r'^(?P<class_>\S+):\s+(?P<id_>.+?)\s*$', line):
        return ParsedLine(line_number, LineType.OBJECT, line, info=object_match.groupdict())

    if property_match := re.match(r'^- (?P<key>\S+):\s+(?P<value>.+?)\s*$', line):
        return ParsedLine(line_number, LineType.PROPERTY, line, info=property_match.groupdict())

    if re.match(r'^\s*#.*$', line):  # comment match (allow whitespace)
        return ParsedLine(line_number, LineType.COMMENT, line, info={})

    if re.match(r'^\s*$', line):  # blank line (allow whitespace)
        return ParsedLine(line_number, LineType.BLANK, line, info={})

    raise InvalidLineException(line_number, f'invalid line `{line}`', LINE_EXPLAINER)


def parse_lines(fault_tree_text: str) -> list[ParsedLine]:
    return [
        parse_line(line_number, line)
        for line_number, line in enumerate(fault_tree_text.splitlines(), start=1)
    ]


def parse_paragraph(chunk: list[ParsedLine]) -> ParsedParagraph:
    if chunk[0].type_ == LineType.OBJECT:
        head_line = chunk[0]
        body_lines = chunk[1:]
    else:
        head_line = None
        body_lines = chunk

    for parsed_line in body_lines:
        if parsed_line.type_ in [LineType.COMMENT, LineType.BLANK]:
            raise ImplementationError

        if parsed_line.type_ == LineType.OBJECT:
            raise SmotheredObjectException(
                parsed_line.number,
                f'missing blank line before declaration of `{parsed_line.info["class_"]}`',
            )

    return ParsedParagraph(object_line=head_line, property_lines=body_lines)


def parse_paragraphs(parsed_lines: list[ParsedLine]) -> list[ParsedParagraph]:
    chunks = []
    latest_chunk = []

    for parsed_line in parsed_lines:
        if parsed_line == parsed_lines[-1] or parsed_line.type_ == LineType.BLANK:
            if latest_chunk:
                chunks.append(latest_chunk)
                latest_chunk = []

        elif parsed_line.type_ in [LineType.OBJECT, LineType.PROPERTY]:
            latest_chunk.append(parsed_line)

    return [
        parse_paragraph(chunk)
        for chunk in chunks
    ]
