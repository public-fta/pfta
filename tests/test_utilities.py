"""
# Public Fault Tree Analyser: test_utilities.py

Unit testing for `utilities.py`.

**Copyright 2025 Conway.**
Licensed under the GNU General Public License v3.0 (GPL-3.0-only).
This is free software with NO WARRANTY etc. etc., see LICENSE.
"""

import math
import unittest

from pfta.utilities import find_cycles, descending_product


class TestUtilities(unittest.TestCase):
    def test_descending_product(self):
        factors_1 = [0.1, 0.3, 0.5, 0.823]
        factors_2 = [0.823, 0.5, 0.3, 0.1]
        self.assertEqual(set(factors_1), set(factors_2))
        self.assertNotEqual(math.prod(factors_1), math.prod(factors_2))
        self.assertEqual(descending_product(factors_1), descending_product(factors_2))

    def test_find_cycles(self):
        self.assertEqual(
            find_cycles({}),
            set(),
        )
        self.assertEqual(
            find_cycles({
                1: {3, 4},
                2: {4},
                3: {4, 5},
                4: {5},
                5: {6, 7},
            }),
            set(),
        )
        self.assertEqual(
            find_cycles({
                1: {1},
                2: {3},
                3: {2}},
            ),
            {(1,), (2, 3)}
        )
        self.assertEqual(
            find_cycles({
                1: {2, 3},
                3: {4},
                4: {5},
                5: {6},
                6: {4},
            }),
            {(4, 5, 6)},
        )
        self.assertEqual(
            find_cycles({
                1: {2},
                2: {5},
                3: {2},
                4: {1, 2},
                5: {4, 6},
                6: {3, 6},
            }),
            {(1, 2, 5, 4), (2, 5, 4), (6,), (2, 5, 6, 3)},
        )
