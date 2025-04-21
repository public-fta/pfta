"""
# Public Fault Tree Analyser: test_boolean.py

Unit testing for `boolean.py`.

**Copyright 2025 Conway.**
Licensed under the GNU General Public License v3.0 (GPL-3.0-only).
This is free software with NO WARRANTY etc. etc., see LICENSE.
"""

import unittest

from pfta.boolean import Term


class TestBoolean(unittest.TestCase):
    def test_term_implies(self):
        # A implies True
        self.assertTrue(Term(1).implies(Term(0)))

        # AB implies A
        self.assertTrue(Term(0b11).implies(Term(0b01)))

        # ABCDE implies ABE
        self.assertTrue(Term(0b11111).implies(Term(0b10011)))

        # E does not imply C (due to C)
        self.assertFalse(Term(0b10000).implies(Term(0b00100)))

        # ADE does not imply ABC (due to BC)
        self.assertFalse(Term(0b11001).implies(Term(0b00111)))

    def test_term_conjunction(self):
        # (Empty conjunction) = True
        self.assertEqual(Term.conjunction(), Term(0))

        # AC = AC
        self.assertEqual(Term.conjunction(Term(0b101)), Term(0b101))

        # True . A = A
        self.assertEqual(Term.conjunction(Term(0), Term(1)), Term(1))

        # ABE . BC = ABCE
        self.assertEqual(Term.conjunction(Term(0b10011), Term(0b00110)), Term(0b10111))

        # C . A . B = ABC
        self.assertEqual(Term.conjunction(Term(0b100), Term(0b001), Term(0b010)), Term(0b111))

        # ABCD . True . A = ABCD
        self.assertEqual(Term.conjunction(Term(0b1111), Term(0b0000), Term(0b0001)), Term(0b1111))
