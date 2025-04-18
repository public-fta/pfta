"""
# Public Fault Tree Analyser: test_parsing.py

Unit testing for `parsing.py`.

**Copyright 2025 Conway**
Licensed under the GNU General Public License v3.0 (GPL-3.0-only).
This is free software with NO WARRANTY etc. etc., see LICENSE.
"""

import unittest

from pfta.parsing import LineType, InvalidLineException, ParsedLine
from pfta.parsing import parse_line


class TestParsing(unittest.TestCase):
    def test_parse_line_object_match(self):
        self.assertEqual(
            parse_line(1, 'Gate: GT-001'),
            ParsedLine(1, LineType.OBJECT, 'Gate: GT-001', info={'class_': 'Gate', 'id_': 'GT-001'}),
        )
        self.assertEqual(
            parse_line(2, 'Event:   EV-002\t\t '),
            ParsedLine(2, LineType.OBJECT, 'Event:   EV-002\t\t ', info={'class_': 'Event', 'id_': 'EV-002'}),
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
            ParsedLine(1, LineType.PROPERTY, '- emotion: HAPPY', info={'key': 'emotion', 'value': 'HAPPY'}),
        )
        self.assertEqual(
            parse_line(2, '- colour: \t  red\t'),
            ParsedLine(2, LineType.PROPERTY, '- colour: \t  red\t', info={'key': 'colour', 'value': 'red'}),
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
            ParsedLine(1, LineType.COMMENT, '# foo', info={}),
        )
        self.assertEqual(
            parse_line(2, '  \t # bar baz'),
            ParsedLine(2, LineType.COMMENT, '  \t # bar baz', info={}),
        )
        self.assertRaises(
            InvalidLineException,
            parse_line, 3, '   missing leading # ',
        )

    def test_parse_line_blank_match(self):
        self.assertEqual(
            parse_line(1, ''),
            ParsedLine(1, LineType.BLANK, '', info={}),
        )
        self.assertEqual(
            parse_line(2, '    '),
            ParsedLine(2, LineType.BLANK, '    ', info={}),
        )
        self.assertEqual(
            parse_line(3, '  \t\t  \t '),
            ParsedLine(3, LineType.BLANK, '  \t\t  \t ', info={}),
        )
