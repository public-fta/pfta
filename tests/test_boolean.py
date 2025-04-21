"""
# Public Fault Tree Analyser: test_boolean.py

Unit testing for `boolean.py`.

**Copyright 2025 Conway.**
Licensed under the GNU General Public License v3.0 (GPL-3.0-only).
This is free software with NO WARRANTY etc. etc., see LICENSE.
"""

import unittest

from pfta.boolean import Term, Expression


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

    def test_term_disjunction(self):
        # (Empty disjunction) = False
        self.assertEqual(Term.disjunction(), Expression())

        # A + True = True
        self.assertEqual(Term.disjunction(Term(1), Term(0)), Expression(Term(0)))

        # A + A + A = A
        self.assertEqual(Term.disjunction(Term(1), Term(1), Term(1)), Expression(Term(1)))

        # AC = AC
        self.assertEqual(Term.disjunction(Term(0b101)), Expression(Term(0b101)))

        # A + B + C = A + B + C
        self.assertEqual(
            Term.disjunction(Term(0b001), Term(0b010), Term(0b100)),
            Expression(Term(0b001), Term(0b010), Term(0b100)),
        )

        # A + AB + BC = A + BC
        self.assertEqual(
            Term.disjunction(Term(0b001), Term(0b011), Term(0b110)),
            Expression(Term(0b001), Term(0b110)),
        )

        # AB + BC + CA + ABC = AB + BC + CA
        self.assertEqual(
            Term.disjunction(Term(0b011), Term(0b110), Term(0b101), Term(0b111)),
            Expression(Term(0b011), Term(0b110), Term(0b101)),
        )

        # God save!
        self.assertEqual(
            Term.disjunction(
                Term(0b000011),  # AB
                Term(0b000110),  # BC
                Term(0b001100),  # CD
                Term(0b010100),  # CE
                Term(0b100000),  # F
                Term(0b000111),  # ABC
                Term(0b001011),  # ABD
                Term(0b010011),  # ABE
                Term(0b001101),  # ACD
                Term(0b010101),  # ACE
                Term(0b011001),  # ADE
                Term(0b001110),  # BCD
                Term(0b010110),  # BCE
                Term(0b011010),  # BDE
                Term(0b011100),  # CDE
                Term(0b001111),  # ABCD
                Term(0b010111),  # ABCE
                Term(0b011011),  # ABDE
                Term(0b011101),  # ACDE
                Term(0b011110),  # BCDE
                Term(0b110101),  # FACE
            ),
            Expression(
                Term(0b000011),  # AB
                Term(0b000110),  # BC
                Term(0b001100),  # CD
                Term(0b010100),  # CE
                Term(0b100000),  # F
                Term(0b011001),  # ADE
                Term(0b011010),  # BDE
            ),
        )

    def test_expression_conjunction(self):
        # (Empty conjunction) = True
        self.assertEqual(
            Expression.conjunction(),
            Expression(Term(0)),
        )

        # True = True
        self.assertEqual(
            Expression.conjunction(Expression(Term(0))),
            Expression(Term(0)),
        )

        # A . True = A
        self.assertEqual(
            Expression.conjunction(Expression(Term(1)), Expression(Term(0))),
            Expression(Term(1)),
        )

        # A . B . C = ABC
        self.assertEqual(
            Expression.conjunction(Expression(Term(0b001)), Expression(Term(0b010)), Expression(Term(0b100))),
            Expression(Term(0b111)),
        )

        # A . AB . ABC = ABC
        self.assertEqual(
            Expression.conjunction(Expression(Term(0b001)), Expression(Term(0b011)), Expression(Term(0b111))),
            Expression(Term(0b111)),
        )

        # A . (A+B) = A
        self.assertEqual(
            Expression.conjunction(Expression(Term(0b01)), Expression(Term(0b01), Term(0b10))),
            Expression(Term(0b01)),
        )

        # (A + B + E) . (A + B + C + D) = A + B + CE + DE
        self.assertEqual(
            Expression.conjunction(
                Expression(Term(0b00001), Term(0b00010), Term(0b10000)),
                Expression(Term(0b00001), Term(0b00010), Term(0b00100), Term(0b01000)),
            ),
            Expression(Term(0b00001), Term(0b00010), Term(0b10100), Term(0b11000)),
        )

        # (A+B) . (A+C) . (A+D) . E = AE + BCDE
        self.assertEqual(
            Expression.conjunction(
                Expression(Term(0b00001), Term(0b00010)),
                Expression(Term(0b00001), Term(0b00100)),
                Expression(Term(0b00001), Term(0b01000)),
                Expression(Term(0b10000)),
            ),
            Expression(Term(0b10001), Term(0b11110)),
        )

    def test_expression_disjunction(self):
        # (Empty disjunction) = False
        self.assertEqual(
            Expression.disjunction(),
            Expression(),
        )

        # A + True = True
        self.assertEqual(
            Expression.disjunction(Expression(Term(1)), Expression(Term(0))),
            Expression(Term(0)),
        )

        # (AB + BC + CA) + ABC = AB + BC + CA
        self.assertEqual(
            Expression.disjunction(
                Expression(Term(0b011), Term(0b110), Term(0b101)),
                Expression(Term(0b111)),
            ),
            Expression(Term(0b011), Term(0b110), Term(0b101)),
        )

        # A + (A + B) + (AB + C) = A + B + C
        self.assertEqual(
            Expression.disjunction(
                Expression(Term(0b001)),
                Expression(Term(0b001), Term(0b010)),
                Expression(Term(0b011), Term(0b100)),
            ),
            Expression(Term(0b001), Term(0b010), Term(0b100)),
        )
