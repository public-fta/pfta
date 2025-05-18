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
    def test_term_division(self):
        # A / True = A
        self.assertEqual(Term(1) / Term(0), Term(1))

        # A / B = A
        self.assertEqual(Term(0b01) / Term(0b10), Term(0b01))

        # AC / True = AC
        self.assertEqual(Term(0b101) / Term(0), Term(0b101))

        # AC / B = AC
        self.assertEqual(Term(0b101) / Term(0b010), Term(0b101))

        # ABCE / BC = AE
        self.assertEqual(Term(0b10111) / Term(0b00110), Term(0b10001))

        # ABCE / BCD = AE
        self.assertEqual(Term(0b10111) / Term(0b01110), Term(0b10001))

    def test_term_order(self):
        self.assertEqual(Term(0).order(), 0)
        self.assertEqual(Term(1).order(), 1)
        self.assertEqual(Term(0b10).order(), 1)
        self.assertEqual(Term(0b10111).order(), 4)

    def test_term_is_vacuous(self):
        self.assertTrue(Term(0).is_vacuous())
        self.assertFalse(Term(1).is_vacuous())
        self.assertFalse(Term(0b10).is_vacuous())
        self.assertFalse(Term(0b10111).is_vacuous())

    def test_term_event_indices(self):
        self.assertEqual(Term(0).event_indices(), ())
        self.assertEqual(Term(1).event_indices(), (0,))
        self.assertEqual(Term(0b1010010).event_indices(), (1, 4, 6,))
        self.assertEqual(Term(2 ** 69420).event_indices(), (69420,))

    def test_term_factors(self):
        self.assertEqual(
            Term(0b10110).factors(),
            (Term(0b00010), Term(0b00100), Term(0b10000)),
        )
        self.assertEqual(
            Term(2 ** 69420 + 2 ** 100 + 2).factors(),
            (Term(2), Term(2 ** 100), Term(2 ** 69420)),
        )

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

    def test_term_create_from_event_index(self):
        self.assertEqual(Term.create_from_event_index(0), Term(0b00001))
        self.assertEqual(Term.create_from_event_index(1), Term(0b00010))
        self.assertEqual(Term.create_from_event_index(2), Term(0b00100))
        self.assertEqual(Term.create_from_event_index(3), Term(0b01000))
        self.assertEqual(Term.create_from_event_index(4), Term(0b10000))
        self.assertEqual(Term.create_from_event_index(69420), Term(2 ** 69420))

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

    def test_term_gcd(self):
        # Empty sequence not allowed
        self.assertRaises(ValueError, Term.gcd)

        # gcd(True) = True
        self.assertEqual(Term.gcd(Term(0)), Term(0))

        # gcd(A) = A
        self.assertEqual(Term.gcd(Term(1)), Term(1))

        # gcd(A, B) = True
        self.assertEqual(Term.gcd(Term(0b01), Term(0b10)), Term(0b00))

        # gcd(A, B, C, D) = True
        self.assertEqual(Term.gcd(Term(0b0001), Term(0b0010), Term(0b0100), Term(0b1000)), Term(0b0000))

        # gcd(AB, B, BC, BD) = B
        self.assertEqual(Term.gcd(Term(0b0011), Term(0b0010), Term(0b0110), Term(0b1010)), Term(0b0010))

        # gcd(ABD, BD, BCD, BD) = BD
        self.assertEqual(Term.gcd(Term(0b1011), Term(0b1010), Term(0b1110), Term(0b1010)), Term(0b1010))

        # gcd(AB, B, BCD, BD) = BD
        self.assertEqual(Term.gcd(Term(0b0011), Term(0b0010), Term(0b1110), Term(0b1010)), Term(0b0010))

        # gcd(AB, BC, CD, DE) = True
        self.assertEqual(Term.gcd(Term(0b00011), Term(0b00110), Term(0b01100), Term(0b11000)), Term(0b00000))

        # gcd(True, ABCD) = True
        self.assertEqual(Term.gcd(Term(0b0000), Term(0b1111)), Term(0b0000))

        # gcd(ACD, ABCD, AD) = AD
        self.assertEqual(Term.gcd(Term(0b1101), Term(0b1111), Term(0b1001)), Term(0b1001))

        # gcd(ABCD, ABCD, ABCD) = ABCD
        self.assertEqual(Term.gcd(Term(0b1111), Term(0b1111), Term(0b1111)), Term(0b1111))

        # gcd(ABCDEFG) = ABCDEFG
        self.assertEqual(Term.gcd(Term(0b1111111)), Term(0b1111111))

    def test_expression_encodings(self):
        self.assertEqual(Expression().encodings(), set())
        self.assertEqual(Expression(Term(0)).encodings(), {0})
        self.assertEqual(Expression(Term(0b0001), Term(0b1000), Term(0b0110)).encodings(), {0b0001, 0b1000, 0b0110})

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

    def test_expression_vote(self):
        # (0 out of 0)() = True
        self.assertEqual(
            Expression.vote(threshold=0),
            Expression(Term(0)),
        )

        # (1 out of 0)() = False
        self.assertEqual(
            Expression.vote(threshold=1),
            Expression(),
        )

        # (0 out of 2)(A, B) = True
        self.assertEqual(
            Expression.vote(Expression(Term(0b01)), Expression(Term(0b10)), threshold=0),
            Expression(Term(0)),
        )

        # (1 out of 2)(A, B) = A + B
        self.assertEqual(
            Expression.vote(Expression(Term(0b01)), Expression(Term(0b10)), threshold=1),
            Expression(Term(0b01), Term(0b10)),
        )

        # (2 out of 2)(A, B) = AB
        self.assertEqual(
            Expression.vote(Expression(Term(0b01)), Expression(Term(0b10)), threshold=2),
            Expression(Term(0b11)),
        )

        # (3 out of 2)(A, B) = False
        self.assertEqual(
            Expression.vote(Expression(Term(0b01)), Expression(Term(0b10)), threshold=3),
            Expression(),
        )

        # (3 out of 5)(A, B, C, D, E)
        self.assertEqual(
            Expression.vote(
                Expression(Term(0b00001)),
                Expression(Term(0b00010)),
                Expression(Term(0b00100)),
                Expression(Term(0b01000)),
                Expression(Term(0b10000)),
                threshold=3,
            ),
            Expression(
                Term(0b00111),  # ABC
                Term(0b01011),  # ABD
                Term(0b10011),  # ABE
                Term(0b01101),  # ACD
                Term(0b10101),  # ACE
                Term(0b11001),  # ADE
                Term(0b01110),  # BCD
                Term(0b10110),  # BCE
                Term(0b11010),  # BDE
                Term(0b11100),  # CDE
            ),
        )
