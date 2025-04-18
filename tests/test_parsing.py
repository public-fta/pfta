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
