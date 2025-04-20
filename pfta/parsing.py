"""
# Public Fault Tree Analyser: parsing.py

Parsing of fault tree text.

**Copyright 2025 Conway.**
Licensed under the GNU General Public License v3.0 (GPL-3.0-only).
This is free software with NO WARRANTY etc. etc., see LICENSE.
"""

import re

from pfta.common import none_aware_dict_eq, natural_repr
from pfta.constants import (
    LineType,
    LINE_EXPLAINER, VALID_CLASSES, CLASS_EXPLAINER,
    BOOLEAN_FROM_STRING, IS_PAGED_EXPLAINER,
    GATE_TYPE_FROM_STRING, GATE_TYPE_EXPLAINER,
    VALID_KEYS_FROM_CLASS, KEY_EXPLAINER_FROM_CLASS,
)
from pfta.woe import FaultTreeTextException, ImplementationError


class InvalidLineException(FaultTreeTextException):
    pass


class SmotheredObjectException(FaultTreeTextException):
    pass


class DanglingPropertyException(FaultTreeTextException):
    pass


class InvalidKeyException(FaultTreeTextException):
    pass


class DuplicateKeyException(FaultTreeTextException):
    pass


class InvalidClassException(FaultTreeTextException):
    pass


class InvalidFloatException(FaultTreeTextException):
    pass


class InvalidBooleanException(FaultTreeTextException):
    pass


class InvalidGateTypeException(FaultTreeTextException):
    pass


class ParsedLine:
    def __init__(self, number: int, type_: LineType, info: dict):
        self.number = number
        self.type_ = type_
        self.info = info

    def __eq__(self, other):
        return none_aware_dict_eq(self, other)

    def __repr__(self):
        return natural_repr(self)


class ParsedParagraph:
    def __init__(self, object_line: ParsedLine | None, property_lines: list[ParsedLine]):
        self.object_line = object_line
        self.property_lines = property_lines

    def __eq__(self, other):
        return none_aware_dict_eq(self, other)

    def __repr__(self):
        return natural_repr(self)


class ParsedAssembly:
    def __init__(self, class_: str, id_: str | None, object_line: ParsedLine | None, property_lines: list[ParsedLine]):
        self.class_ = class_
        self.id_ = id_
        self.object_line = object_line
        self.property_lines = property_lines

    def __eq__(self, other):
        return none_aware_dict_eq(self, other)

    def __repr__(self):
        return natural_repr(self)

    def last_line_number(self) -> int:
        if self.property_lines:
            return self.property_lines[-1].number

        if self.object_line:
            return self.object_line.number

        return 1


def split_by_comma(string: str) -> list[str]:
    string = re.sub(r'\s*,\s*\Z', '', string)  # observe one trailing comma

    if not string:
        return []

    return re.split(r'\s*,\s*', string)


def parse_line(line_number: int, line: str) -> ParsedLine:
    if object_match := re.match(r'^(?P<class>\S+):\s+(?P<id>.+?)\s*$', line):
        return ParsedLine(line_number, LineType.OBJECT, info=object_match.groupdict())

    if property_match := re.match(r'^- (?P<key>\S+):\s+(?P<value>.+?)\s*$', line):
        return ParsedLine(line_number, LineType.PROPERTY, info=property_match.groupdict())

    if re.match(r'^\s*#.*$', line):  # comment match (allow whitespace)
        return ParsedLine(line_number, LineType.COMMENT, info={})

    if re.match(r'^\s*$', line):  # blank line (allow whitespace)
        return ParsedLine(line_number, LineType.BLANK, info={})

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
        if parsed_line.type_ in (LineType.COMMENT, LineType.BLANK):
            raise ImplementationError('comment lines and blank lines should not appear in chunk')

        if parsed_line.type_ == LineType.OBJECT:
            raise SmotheredObjectException(
                parsed_line.number,
                f'missing blank line before declaration of `{parsed_line.info["class"]}`',
            )

    return ParsedParagraph(object_line=head_line, property_lines=body_lines)


def parse_paragraphs(parsed_lines: list[ParsedLine]) -> list[ParsedParagraph]:
    chunks = []
    latest_chunk = []

    for parsed_line in parsed_lines:
        if parsed_line.type_ in (LineType.OBJECT, LineType.PROPERTY):
            latest_chunk.append(parsed_line)

        if parsed_line == parsed_lines[-1] or parsed_line.type_ == LineType.BLANK:
            if latest_chunk:
                chunks.append(latest_chunk)
                latest_chunk = []

    return [
        parse_paragraph(chunk)
        for chunk in chunks
    ]


def parse_assembly(parsed_paragraph: ParsedParagraph, is_first_paragraph: bool) -> ParsedAssembly:
    object_line = parsed_paragraph.object_line
    property_lines = parsed_paragraph.property_lines

    if object_line is None:
        if not is_first_paragraph:
            dangling_line = property_lines[0]
            raise DanglingPropertyException(
                dangling_line.number,
                f'missing object declaration before setting property `{dangling_line.info["key"]}`',
            )

        class_ = 'FaultTree'
        id_ = None
    else:
        class_ = object_line.info['class']
        id_ = object_line.info['id']

        if class_ not in VALID_CLASSES:
            raise InvalidClassException(object_line.number, f'invalid class `{class_}`', CLASS_EXPLAINER)

    seen_keys = set()

    for parsed_line in property_lines:
        try:
            valid_keys = VALID_KEYS_FROM_CLASS[class_]
        except KeyError:
            raise ImplementationError('class inconsistent with dictionary of valid keys')

        key = parsed_line.info['key']

        if key not in valid_keys:
            raise InvalidKeyException(
                parsed_line.number,
                f'invalid key `{key}` for a property setting under class `{class_}`',
                KEY_EXPLAINER_FROM_CLASS[class_]
            )

        if key in seen_keys:
            raise DuplicateKeyException(
                parsed_line.number,
                f'duplicate key `{key}` for a property setting under class `{class_}`',
            )

        seen_keys.add(key)

    return ParsedAssembly(class_, id_, object_line, property_lines)


def parse_assemblies(parsed_paragraphs: list[ParsedParagraph]) -> list[ParsedAssembly]:
    return [
        parse_assembly(parsed_paragraph, is_first_paragraph=parsed_paragraph == parsed_paragraphs[0])
        for parsed_paragraph in parsed_paragraphs
    ]


def parse_fault_tree_properties(parsed_assembly: ParsedAssembly) -> dict:
    properties = {}

    for parsed_line in parsed_assembly.property_lines:
        key = parsed_line.info['key']
        value = parsed_line.info['value']

        if key == 'time_unit':
            properties['time_unit'] = value
            continue

        if key == 'time':
            times = []
            times_raw = []

            for time_raw in split_by_comma(value):
                try:
                    times.append(float(time_raw))
                except ValueError:
                    raise InvalidFloatException(parsed_line.number, f'unable to convert `{time_raw}` to float')

                times_raw.append(time_raw)

            properties['times'] = times
            properties['times_raw'] = times_raw
            properties['times_line_number'] = parsed_line.number
            continue

        raise ImplementationError(f'bad key `{key}`')

    return properties


def parse_event_properties(parsed_assembly: ParsedAssembly) -> dict:
    properties = {}

    for parsed_line in parsed_assembly.property_lines:
        key = parsed_line.info['key']
        value = parsed_line.info['value']

        if key in ('label', 'comment'):
            properties[key] = value
            continue

        if key == 'probability':
            try:
                properties['probability'] = float(value)  # TODO: check value / handle distributions
            except ValueError:
                raise InvalidFloatException(parsed_line.number, f'unable to convert `{value}` to float')
            continue

        if key == 'intensity':
            try:
                properties['intensity'] = float(value)  # TODO: check value / handle distributions
            except ValueError:
                raise InvalidFloatException(parsed_line.number, f'unable to convert `{value}` to float')
            continue

        raise ImplementationError(f'bad key `{key}`')

    return properties


def parse_gate_properties(parsed_assembly: ParsedAssembly) -> dict:
    properties = {}

    for parsed_line in parsed_assembly.property_lines:
        key = parsed_line.info['key']
        value = parsed_line.info['value']

        if key in ('label', 'comment'):
            properties[key] = value
            continue

        if key == 'is_paged':
            try:
                properties['is_paged'] = BOOLEAN_FROM_STRING[value]
            except KeyError:
                raise InvalidBooleanException(parsed_line.number, f'invalid value `{value}`', IS_PAGED_EXPLAINER)
            continue

        if key == 'type':
            try:
                properties['type'] = GATE_TYPE_FROM_STRING[value]
            except KeyError:
                raise InvalidGateTypeException(parsed_line.number, f'invalid value `{value}`', GATE_TYPE_EXPLAINER)
            continue

        if key == 'inputs':
            properties['input_ids'] = split_by_comma(value)
            continue

        raise ImplementationError(f'bad key `{key}`')

    return properties
