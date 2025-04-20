"""
# Public Fault Tree Analyser: test_parsing.py

Unit testing for `parsing.py`.

**Copyright 2025 Conway.**
Licensed under the GNU General Public License v3.0 (GPL-3.0-only).
This is free software with NO WARRANTY etc. etc., see LICENSE.
"""

import unittest

from pfta.parsing import (
    InvalidLineException, SmotheredObjectException, DanglingPropertyException,
    InvalidKeyException, DuplicateKeyException, InvalidClassException,
    InvalidFloatException, NonPositiveValueException,
    ParsedLine, ParsedParagraph, ParsedAssembly,
    split_by_comma,
    parse_line, parse_paragraph, parse_assembly,
    parse_fault_tree_properties, parse_event_properties,
)
from pfta.constants import LineType


class TestParsing(unittest.TestCase):
    def test_split_by_comma(self):
        self.assertEqual(split_by_comma(''), [])
        self.assertEqual(split_by_comma(','), [])
        self.assertEqual(split_by_comma(' \t , \t'), [])

        self.assertEqual(split_by_comma(',,'), ['', ''])
        self.assertEqual(split_by_comma(', ,'), ['', ''])

        self.assertEqual(split_by_comma('A, B, C'), ['A', 'B', 'C'])
        self.assertEqual(split_by_comma('A, B, C,'), ['A', 'B', 'C'])
        self.assertEqual(split_by_comma('A, B, C,,'), ['A', 'B', 'C', ''])

    def test_parse_line_object_match(self):
        self.assertEqual(
            parse_line(1, 'Gate: GT-001'),
            ParsedLine(1, LineType.OBJECT, info={'class_': 'Gate', 'id_': 'GT-001'}),
        )
        self.assertEqual(
            parse_line(2, 'Event:   EV-002\t\t '),
            ParsedLine(2, LineType.OBJECT, info={'class_': 'Event', 'id_': 'EV-002'}),
        )
        self.assertRaises(
            InvalidLineException,
            parse_line, 3, 'Gate',  # incomplete
        )
        self.assertRaises(
            InvalidLineException,
            parse_line, 4, 'Gate:',  # incomplete
        )
        self.assertRaises(
            InvalidLineException,
            parse_line, 5, 'Gate: ',  # incomplete
        )
        self.assertRaises(
            InvalidLineException,
            parse_line, 6, ' Gate: GT-006',  # leading whitespace
        )
        self.assertRaises(
            InvalidLineException,
            parse_line, 7, 'Gate : GT-007',  # whitespace before colon
        )
        self.assertRaises(
            InvalidLineException,
            parse_line, 8, 'Ga te: GT-008',  # whitespace in class
        )

    def test_parse_line_property_match(self):
        self.assertEqual(
            parse_line(1, '- emotion: HAPPY'),
            ParsedLine(1, LineType.PROPERTY, info={'key': 'emotion', 'value': 'HAPPY'}),
        )
        self.assertEqual(
            parse_line(2, '- colour: \t  red\t'),
            ParsedLine(2, LineType.PROPERTY, info={'key': 'colour', 'value': 'red'}),
        )
        self.assertRaises(
            InvalidLineException,
            parse_line, 3, '- age',  # incomplete
        )
        self.assertRaises(
            InvalidLineException,
            parse_line, 4, '- age:',  # incomplete
        )
        self.assertRaises(
            InvalidLineException,
            parse_line, 5, '- age: ',  # incomplete
        )
        self.assertRaises(
            InvalidLineException,
            parse_line, 6, ' - age: 60',  # leading whitespace
        )
        self.assertRaises(
            InvalidLineException,
            parse_line, 7, '- age : 70',  # whitespace before colon
        )
        self.assertRaises(
            InvalidLineException,
            parse_line, 8, '- a ge: 80',  # whitespace in key
        )
        self.assertRaises(
            InvalidLineException,
            parse_line, 9, '-  age: 90',  # double-space before key
        )

    def test_parse_line_comment_match(self):
        self.assertEqual(
            parse_line(1, '# foo'),
            ParsedLine(1, LineType.COMMENT, info={}),
        )
        self.assertEqual(
            parse_line(2, '  \t # bar baz'),
            ParsedLine(2, LineType.COMMENT, info={}),
        )
        self.assertRaises(
            InvalidLineException,
            parse_line, 3, '   missing leading # ',
        )

    def test_parse_line_blank_match(self):
        self.assertEqual(
            parse_line(1, ''),
            ParsedLine(1, LineType.BLANK, info={}),
        )
        self.assertEqual(
            parse_line(2, '    '),
            ParsedLine(2, LineType.BLANK, info={}),
        )
        self.assertEqual(
            parse_line(3, '  \t\t  \t '),
            ParsedLine(3, LineType.BLANK, info={}),
        )

    def test_parse_paragraph(self):
        # Full paragraph
        self.assertEqual(
            parse_paragraph([
                ParsedLine(1, LineType.OBJECT, info={'class_': 'Person', 'id_': 'John'}),
                ParsedLine(2, LineType.PROPERTY, info={'key': 'emotion', 'value': 'HAPPY'}),
                ParsedLine(3, LineType.PROPERTY, info={'key': 'age', 'value': '50'}),
            ]),
            ParsedParagraph(
                object_line=ParsedLine(1, LineType.OBJECT, info={'class_': 'Person', 'id_': 'John'}),
                property_lines=[
                    ParsedLine(2, LineType.PROPERTY, info={'key': 'emotion', 'value': 'HAPPY'}),
                    ParsedLine(3, LineType.PROPERTY, info={'key': 'age', 'value': '50'}),
                ],
            ),
        )

        # Paragraph with no object declaration
        self.assertEqual(
            parse_paragraph([
                ParsedLine(2, LineType.PROPERTY, info={'key': 'emotion', 'value': 'HAPPY'}),
                ParsedLine(3, LineType.PROPERTY, info={'key': 'age', 'value': '50'}),
            ]),
            ParsedParagraph(
                object_line=None,
                property_lines=[
                    ParsedLine(2, LineType.PROPERTY, info={'key': 'emotion', 'value': 'HAPPY'}),
                    ParsedLine(3, LineType.PROPERTY, info={'key': 'age', 'value': '50'}),
                ],
            ),
        )

        # Paragraph with no property settings
        self.assertEqual(
            parse_paragraph([
                ParsedLine(1, LineType.OBJECT, info={'class_': 'Person', 'id_': 'John'}),
            ]),
            ParsedParagraph(
                object_line=ParsedLine(1, LineType.OBJECT, info={'class_': 'Person', 'id_': 'John'}),
                property_lines=[],
            ),
        )

        # Smothered object declaration (by another)
        self.assertRaises(
            SmotheredObjectException,
            parse_paragraph,
            [
                ParsedLine(1, LineType.OBJECT, info={'class_': 'Person', 'id_': 'John'}),
                ParsedLine(2, LineType.OBJECT, info={'class_': 'Person', 'id_': 'Dave'}),
            ],
        )

        # Smothered object declaration (by a property setting)
        self.assertRaises(
            SmotheredObjectException,
            parse_paragraph,
            [
                ParsedLine(1, LineType.PROPERTY, info={'key': 'emotion', 'value': 'HAPPY'}),
                ParsedLine(2, LineType.OBJECT, info={'class_': 'Person', 'id_': 'Dave'}),
            ],
        )

    def test_parse_assembly(self):
        # Reasonable fault tree
        self.assertEqual(
            parse_assembly(
                ParsedParagraph(
                    object_line=None,
                    property_lines=[
                        ParsedLine(2, LineType.PROPERTY, info={'key': 'time', 'value': '1'}),
                        ParsedLine(3, LineType.PROPERTY, info={'key': 'time_unit', 'value': 'h'}),
                    ],
                ),
                is_first_paragraph=True,
            ),
            ParsedAssembly(
                class_='FaultTree',
                id_=None,
                object_line=None,
                property_lines=[
                    ParsedLine(2, LineType.PROPERTY, info={'key': 'time', 'value': '1'}),
                    ParsedLine(3, LineType.PROPERTY, info={'key': 'time_unit', 'value': 'h'}),
                ],
            ),
        )

        # Reasonable event
        self.assertEqual(
            parse_assembly(
                ParsedParagraph(
                    object_line=ParsedLine(1, LineType.OBJECT, info={'class_': 'Event', 'id_': 'EV-001'}),
                    property_lines=[
                        ParsedLine(2, LineType.PROPERTY, info={'key': 'label', 'value': 'Weather is cloudy'}),
                        ParsedLine(3, LineType.PROPERTY, info={'key': 'probability', 'value': '0.2'}),
                    ],
                ),
                is_first_paragraph=True,
            ),
            ParsedAssembly(
                class_='Event',
                id_='EV-001',
                object_line=ParsedLine(1, LineType.OBJECT, info={'class_': 'Event', 'id_': 'EV-001'}),
                property_lines=[
                    ParsedLine(2, LineType.PROPERTY, info={'key': 'label', 'value': 'Weather is cloudy'}),
                    ParsedLine(3, LineType.PROPERTY, info={'key': 'probability', 'value': '0.2'}),
                ],
            ),
        )

        # Reasonable gate
        self.assertEqual(
            parse_assembly(
                ParsedParagraph(
                    object_line=ParsedLine(1, LineType.OBJECT, info={'class_': 'Gate', 'id_': 'GT-001'}),
                    property_lines=[
                        ParsedLine(2, LineType.PROPERTY, info={'key': 'label', 'value': 'Old man yells at cloud'}),
                        ParsedLine(3, LineType.PROPERTY, info={'key': 'inputs', 'value': 'EV-001, EV-002'}),
                    ],
                ),
                is_first_paragraph=True,
            ),
            ParsedAssembly(
                class_='Gate',
                id_='GT-001',
                object_line=ParsedLine(1, LineType.OBJECT, info={'class_': 'Gate', 'id_': 'GT-001'}),
                property_lines=[
                    ParsedLine(2, LineType.PROPERTY, info={'key': 'label', 'value': 'Old man yells at cloud'}),
                    ParsedLine(3, LineType.PROPERTY, info={'key': 'inputs', 'value': 'EV-001, EV-002'}),
                ],
            ),
        )

        # Dangling property
        self.assertRaises(
            DanglingPropertyException,
            parse_assembly,
            ParsedParagraph(
                object_line=None,
                property_lines=[
                    ParsedLine(20, LineType.PROPERTY, info={'key': 'time', 'value': '1'}),
                    ParsedLine(21, LineType.PROPERTY, info={'key': 'time_unit', 'value': 'h'}),
                ],
            ),
            is_first_paragraph=False,
        )

        # Invalid key
        self.assertRaises(
            InvalidKeyException,
            parse_assembly,
            ParsedParagraph(
                object_line=None,
                property_lines=[ParsedLine(1, LineType.PROPERTY, info={'key': 'age', 'value': '60'})],
            ),
            is_first_paragraph=True,
        )
        self.assertRaises(
            InvalidKeyException,
            parse_assembly,
            ParsedParagraph(
                object_line=ParsedLine(9, LineType.OBJECT, info={'class_': 'Event', 'id_': 'EV-001'}),
                property_lines=[ParsedLine(10, LineType.PROPERTY, info={'key': 'age', 'value': '60'})],
            ),
            is_first_paragraph=False,
        )
        self.assertRaises(
            InvalidKeyException,
            parse_assembly,
            ParsedParagraph(
                object_line=ParsedLine(9, LineType.OBJECT, info={'class_': 'Gate', 'id_': 'GT-001'}),
                property_lines=[ParsedLine(10, LineType.PROPERTY, info={'key': 'iNpUTs', 'value': 'EV-001, EV-002'})],
            ),
            is_first_paragraph=False,
        )

        # Duplicate key
        self.assertRaises(
            DuplicateKeyException,
            parse_assembly,
            ParsedParagraph(
                object_line=None,
                property_lines=[
                    ParsedLine(1, LineType.PROPERTY, info={'key': 'time', 'value': '1'}),
                    ParsedLine(2, LineType.PROPERTY, info={'key': 'time', 'value': '1'}),
                ],
            ),
            is_first_paragraph=True,
        )

        # Invalid class
        self.assertRaises(
            InvalidClassException,
            parse_assembly,
            ParsedParagraph(
                object_line=ParsedLine(1, LineType.OBJECT, info={'class_': 'FaultTree', 'id_': 'MASTER'}),
                property_lines=[],
            ),
            is_first_paragraph=True,
        )
        self.assertRaises(
            InvalidClassException,
            parse_assembly,
            ParsedParagraph(
                object_line=ParsedLine(100, LineType.OBJECT, info={'class_': 'foo', 'id_': 'bar'}),
                property_lines=[],
            ),
            is_first_paragraph=False,
        )

    def test_parse_fault_tree_properties(self):
        # Allow trailing comma
        try:
            parse_fault_tree_properties(
                ParsedAssembly(
                    class_='FaultTree',
                    id_=None,
                    object_line=None,
                    property_lines=[
                        ParsedLine(1, LineType.PROPERTY, info={'key': 'time', 'value': '3.1,'})
                    ],
                ),
            )
        except InvalidFloatException:
            self.fail('InvalidFloatException should not be raised')

        # Observe only one trailing comma
        self.assertRaises(
            InvalidFloatException,
            parse_fault_tree_properties,
            ParsedAssembly(
                class_='FaultTree',
                id_=None,
                object_line=None,
                property_lines=[
                    ParsedLine(1, LineType.PROPERTY, info={'key': 'time', 'value': '3.1,,'})
                ],
            ),
        )

        # Invalid float
        self.assertRaises(
            InvalidFloatException,
            parse_fault_tree_properties,
            ParsedAssembly(
                class_='FaultTree',
                id_=None,
                object_line=None,
                property_lines=[
                    ParsedLine(1, LineType.PROPERTY, info={'key': 'time', 'value': '3.1, foo'})
                ],
            ),
        )

        # Non-positive time
        self.assertRaises(
            NonPositiveValueException,
            parse_fault_tree_properties,
            ParsedAssembly(
                class_='FaultTree',
                id_=None,
                object_line=None,
                property_lines=[
                    ParsedLine(1, LineType.PROPERTY, info={'key': 'time', 'value': '0.'})
                ],
            ),
        )
        self.assertRaises(
            NonPositiveValueException,
            parse_fault_tree_properties,
            ParsedAssembly(
                class_='FaultTree',
                id_=None,
                object_line=None,
                property_lines=[
                    ParsedLine(1, LineType.PROPERTY, info={'key': 'time', 'value': '-1'})
                ],
            ),
        )
        self.assertRaises(
            NonPositiveValueException,
            parse_fault_tree_properties,
            ParsedAssembly(
                class_='FaultTree',
                id_=None,
                object_line=None,
                property_lines=[
                    ParsedLine(1, LineType.PROPERTY, info={'key': 'time', 'value': '3, 4, -5'})
                ],
            ),
        )

    def test_parse_event_properties(self):
        # Invalid float
        self.assertRaises(
            InvalidFloatException,
            parse_event_properties,
            ParsedAssembly(
                class_='Event',
                id_='EV-001',
                object_line=ParsedLine(4, LineType.OBJECT, info={'class_': 'Event', 'id_': 'EV-001'}),
                property_lines=[
                    ParsedLine(5, LineType.PROPERTY, info={'key': 'intensity', 'value': 'bar'})
                ],
            ),
        )
