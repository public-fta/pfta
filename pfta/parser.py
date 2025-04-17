"""
# Public Fault Tree Analyser: parser.py

Parser of fault tree text.

**Copyright 2025 Conway**
Licensed under the GNU General Public License v3.0 (GPL-3.0-only).
This is free software with NO WARRANTY etc. etc., see LICENSE.
"""

import re
from enum import Enum


class FaultTreeTextException(Exception):
    def __init__(self, line_number: int, message: str, explainer: str):
        self.line_number = line_number
        self.message = message
        self.explainer = explainer


class LineType(Enum):
    OBJECT_DECLARATION = 0
    PROPERTY_SETTING = 1
    BLANK_LINE = 2
    COMMENT_LINE = 3


class ParsedLine:
    LINE_EXPLAINER = '\n'.join([
        'A line must have one of the following forms:',
        '    Event: <identifier>    (an Event declaration)',
        '    Gate: <identifier>     (an Gate declaration)',
        '    - <key>: <value>       (a property setting)',
        '    # <comment>            (a comment)',
        '    <blank line>           (used before the next declarations)',
    ])
    ID_EXPLAINER = 'An identifier must contain only ASCII letters, digits, underscores, and hyphens.'

    def __init__(self, number: int, line: str, type_: LineType, info: dict):
        self.number = number
        self.line = line
        self.type_ = type_
        self.info = info

    class InvalidIdException(FaultTreeTextException):
        pass

    class InvalidLineException(FaultTreeTextException):
        pass


def is_valid_id(id_: str) -> bool:
    return bool(re.fullmatch('[a-z0-9_-]', id_, flags=re.IGNORECASE))


def parse_line(line_number: int, line: str) -> ParsedLine:
    if object_match := re.match(r'^(?P<class_>Event|Gate):\s+(?P<id_>.+?)\s*$', line):
        class_ = object_match.group('class_')
        id_ = object_match.group('id_')

        if not is_valid_id(id_):  # TODO: move to enact_line
            raise ParsedLine.InvalidIdException(line_number, f'invalid identifier `{id_}`', ParsedLine.ID_EXPLAINER)

        return ParsedLine(line_number, line, LineType.OBJECT_DECLARATION, info={'class_': class_, 'id_': id_})

    if property_match := re.match(r'^- (?P<key>\S+):\s+(?P<value>.+?)\s*$', line):
        key = property_match.group('key')
        value = property_match.group('value')

        return ParsedLine(line_number, line, LineType.PROPERTY_SETTING, info={'key': key, 'value': value})

    if re.match('^\s*#.*$', line):  # comment match
        return ParsedLine(line_number, line, LineType.COMMENT_LINE, info={})

    if re.match('^\s*$', line):  # blank line
        return ParsedLine(line_number, line, LineType.BLANK_LINE, info={})

    raise ParsedLine.InvalidLineException(line_number, f'invalid line `{line}`', ParsedLine.LINE_EXPLAINER)


def parse(fault_tree_text: str):
    for line_number, line in enumerate(fault_tree_text.splitlines(), start=1):
        parsed_line = parse_line(line_number, line)
