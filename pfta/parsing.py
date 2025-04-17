"""
# Public Fault Tree Analyser: parsing.py

Parsing of fault tree text.

**Copyright 2025 Conway**
Licensed under the GNU General Public License v3.0 (GPL-3.0-only).
This is free software with NO WARRANTY etc. etc., see LICENSE.
"""

import re
from enum import Enum

from pfta.exceptions import FaultTreeTextException


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


class ParsedLine:
    def __init__(self, number: int, type_: LineType, content: str, info: dict):
        self.number = number
        self.type_ = type_
        self.content = content
        self.info = info

    class InvalidLineException(FaultTreeTextException):
        pass


def parse_line(line_number: int, line: str) -> ParsedLine:
    if object_match := re.match(r'^(?P<class_>\S+):\s+(?P<id_>.+?)\s*$', line):
        return ParsedLine(line_number, LineType.OBJECT, line, info=object_match.groupdict())

    if property_match := re.match(r'^- (?P<key>\S+):\s+(?P<value>.+?)\s*$', line):
        return ParsedLine(line_number, LineType.PROPERTY, line, info=property_match.groupdict())

    if re.match('^\s*#.*$', line):  # comment match (allow whitespace)
        return ParsedLine(line_number, LineType.COMMENT, line, info={})

    if re.match('^\s*$', line):  # blank line (allow whitespace)
        return ParsedLine(line_number, LineType.BLANK, line, info={})

    raise ParsedLine.InvalidLineException(line_number, f'invalid line `{line}`', LINE_EXPLAINER)


def parse_lines(fault_tree_text: str) -> list[ParsedLine]:
    return [
        parse_line(line_number, line)
        for line_number, line in enumerate(fault_tree_text.splitlines(), start=1)
    ]
