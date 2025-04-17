"""
# Public Fault Tree Analyser: parser.py

Parser of fault tree text.

**Copyright 2025 Conway**
Licensed under the GNU General Public License v3.0 (GPL-3.0-only).
This is free software with NO WARRANTY etc. etc., see LICENSE.
"""

import re


LINE_EXPLAINER = '\n'.join([
    'A line must have one of the following forms:',
    '    <class>: <identifier>  (an object declaration)',
    '    - <key>: <value>       (a property setting)',
    '    # <comment>            (a comment)',
    '    <blank line>           (used before the next declaration)',
])


class FaultTreeTextException(Exception):
    def __init__(self, line_number: int, message: str, explainer: str):
        self.line_number = line_number
        self.message = message
        self.explainer = explainer


class ParsedLine:
    def __init__(self, number: int, content: str, info: dict):
        self.number = number
        self.content = content
        self.info = info

    class InvalidIdException(FaultTreeTextException):
        pass

    class InvalidLineException(FaultTreeTextException):
        pass


class ParsedObjectLine(ParsedLine):
    pass


class ParsedPropertyLine(ParsedLine):
    pass


class ParsedCommentLine(ParsedLine):
    pass


class ParsedBlankLine(ParsedLine):
    pass


def is_valid_class(class_: str) -> bool:
    return class_ in {'Event', 'Gate'}


def is_valid_id(id_: str) -> bool:
    return bool(re.fullmatch('[a-z0-9_-]', id_, flags=re.IGNORECASE))


def parse_line(line_number: int, line: str) -> ParsedLine:
    if object_match := re.match(r'^(?P<class_>\S+):\s+(?P<id_>.+?)\s*$', line):
        return ParsedObjectLine(line_number, line, info=object_match.groupdict())

    if property_match := re.match(r'^- (?P<key>\S+):\s+(?P<value>.+?)\s*$', line):
        return ParsedPropertyLine(line_number, line, info=property_match.groupdict())

    if re.match('^\s*#.*$', line):  # comment match (allow whitespace)
        return ParsedCommentLine(line_number, line, info={})

    if re.match('^\s*$', line):  # blank line (allow whitespace)
        return ParsedBlankLine(line_number, line, info={})

    raise ParsedLine.InvalidLineException(line_number, f'invalid line `{line}`', LINE_EXPLAINER)


def parse_lines(fault_tree_text: str) -> list[ParsedLine]:
    return [
        parse_line(line_number, line)
        for line_number, line in enumerate(fault_tree_text.splitlines(), start=1)
    ]
