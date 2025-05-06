"""
# Public Fault Tree Analyser: test_utilities.py

Unit testing for `utilities.py`.

**Copyright 2025 Conway.**
Licensed under the GNU General Public License v3.0 (GPL-3.0-only).
This is free software with NO WARRANTY etc. etc., see LICENSE.
"""

import math
import unittest

from pfta.utilities import format_number, descending_product, descending_sum, find_cycles


class TestUtilities(unittest.TestCase):
    def test_format_number(self):
        self.assertEqual(format_number(None), None)
        self.assertEqual(format_number(float('inf')), 'inf')
        self.assertEqual(format_number(float('-inf')), '-inf')
        self.assertEqual(format_number(float('nan')), 'nan')

        self.assertRaises(ValueError, format_number, 1)
        self.assertRaises(ValueError, format_number, 1, decimal_places=4, significant_figures=3)
        self.assertRaises(ValueError, format_number, 1, decimal_places=-1)
        self.assertRaises(ValueError, format_number, 1, significant_figures=0)

        self.assertEqual(format_number(0, decimal_places=3), '0')
        self.assertEqual(format_number(0., decimal_places=3), '0')
        self.assertEqual(format_number(-0., decimal_places=3), '0')

        self.assertEqual(format_number(0, significant_figures=3, return_plain_zero=True), '0')
        self.assertEqual(format_number(0., significant_figures=3, return_plain_zero=True), '0')
        self.assertEqual(format_number(-0., significant_figures=3, return_plain_zero=True), '0')

        self.assertEqual(format_number(0, decimal_places=0, return_plain_zero=False), '0')
        self.assertEqual(format_number(0, decimal_places=1, return_plain_zero=False), '0.0')
        self.assertEqual(format_number(0, decimal_places=2, return_plain_zero=False), '0.00')
        self.assertEqual(format_number(0, decimal_places=3, return_plain_zero=False), '0.000')
        self.assertEqual(format_number(0., decimal_places=0, return_plain_zero=False), '0')
        self.assertEqual(format_number(0., decimal_places=1, return_plain_zero=False), '0.0')
        self.assertEqual(format_number(0., decimal_places=2, return_plain_zero=False), '0.00')
        self.assertEqual(format_number(0., decimal_places=3, return_plain_zero=False), '0.000')
        self.assertEqual(format_number(-0., decimal_places=0, return_plain_zero=False), '-0')
        self.assertEqual(format_number(-0., decimal_places=1, return_plain_zero=False), '-0.0')
        self.assertEqual(format_number(-0., decimal_places=2, return_plain_zero=False), '-0.00')
        self.assertEqual(format_number(-0., decimal_places=3, return_plain_zero=False), '-0.000')

        self.assertEqual(format_number(0, significant_figures=1, return_plain_zero=False), '0')
        self.assertEqual(format_number(0, significant_figures=2, return_plain_zero=False), '0.0')
        self.assertEqual(format_number(0, significant_figures=3, return_plain_zero=False), '0.00')
        self.assertEqual(format_number(0., significant_figures=1, return_plain_zero=False), '0')
        self.assertEqual(format_number(0., significant_figures=2, return_plain_zero=False), '0.0')
        self.assertEqual(format_number(0., significant_figures=3, return_plain_zero=False), '0.00')
        self.assertEqual(format_number(-0., significant_figures=1, return_plain_zero=False), '-0')
        self.assertEqual(format_number(-0., significant_figures=2, return_plain_zero=False), '-0.0')
        self.assertEqual(format_number(-0., significant_figures=3, return_plain_zero=False), '-0.00')

        self.assertNotEqual(str(0.1 + 0.2), '0.3')
        self.assertEqual(format_number(0.1 + 0.2, decimal_places=1), '0.3')
        self.assertEqual(format_number(0.1 + 0.2, significant_figures=1), '0.3')

        self.assertEqual(format_number(89640, decimal_places=0), '89640')
        self.assertEqual(format_number(89640, decimal_places=1), '89640.0')
        self.assertEqual(format_number(89640, decimal_places=2), '89640.00')
        self.assertEqual(format_number(-89640, decimal_places=3), '-89640.000')
        self.assertEqual(format_number(-89640, decimal_places=4), '-89640.0000')
        self.assertEqual(format_number(-89640, decimal_places=5), '-89640.00000')
        self.assertEqual(format_number(89640, significant_figures=1), '9E+4')
        self.assertEqual(format_number(89640, significant_figures=2), '9.0E+4')
        self.assertEqual(format_number(-89640, significant_figures=3), '-8.96E+4')
        self.assertEqual(format_number(-89640, significant_figures=4), '-8.964E+4')
        self.assertEqual(format_number(-89640, significant_figures=5), '-8.9640E+4')

        self.assertEqual(format_number(69.42069, decimal_places=0), '69')
        self.assertEqual(format_number(69.42069, decimal_places=1), '69.4')
        self.assertEqual(format_number(69.42069, decimal_places=2), '69.42')
        self.assertEqual(format_number(69.42069, decimal_places=3), '69.421')
        self.assertEqual(format_number(-69.42069, decimal_places=4), '-69.4207')
        self.assertEqual(format_number(-69.42069, decimal_places=5), '-69.42069')
        self.assertEqual(format_number(-69.42069, decimal_places=6), '-69.420690')
        self.assertEqual(format_number(69.42069, significant_figures=1), '7E+1')
        self.assertEqual(format_number(69.42069, significant_figures=2), '69')
        self.assertEqual(format_number(69.42069, significant_figures=3), '69.4')
        self.assertEqual(format_number(69.42069, significant_figures=4), '69.42')
        self.assertEqual(format_number(69.42069, significant_figures=5), '69.421')
        self.assertEqual(format_number(-69.42069, significant_figures=6), '-69.4207')
        self.assertEqual(format_number(-69.42069, significant_figures=7), '-69.42069')
        self.assertEqual(format_number(-69.42069, significant_figures=8), '-69.420690')

        self.assertEqual(format_number(0.00123456789, decimal_places=0), '0')
        self.assertEqual(format_number(0.00123456789, decimal_places=1), '0.0')
        self.assertEqual(format_number(0.00123456789, decimal_places=2), '0.00')
        self.assertEqual(format_number(0.00123456789, decimal_places=3), '0.001')
        self.assertEqual(format_number(0.00123456789, decimal_places=4), '0.0012')
        self.assertEqual(format_number(0.00123456789, decimal_places=5), '0.00123')
        self.assertEqual(format_number(0.00123456789, decimal_places=6), '0.001235')
        self.assertEqual(format_number(0.00123456789, decimal_places=7), '0.0012346')
        self.assertEqual(format_number(0.00123456789, decimal_places=8), '0.00123457')
        self.assertEqual(format_number(0.00123456789, decimal_places=9), '0.001234568')
        self.assertEqual(format_number(-0.00123456789, decimal_places=10), '-0.0012345679')
        self.assertEqual(format_number(-0.00123456789, decimal_places=11), '-0.00123456789')
        self.assertEqual(format_number(-0.00123456789, decimal_places=12), '-0.001234567890')
        self.assertEqual(format_number(0.00123456789, significant_figures=1), '1E-3')
        self.assertEqual(format_number(0.00123456789, significant_figures=2), '1.2E-3')
        self.assertEqual(format_number(0.00123456789, significant_figures=3), '1.23E-3')
        self.assertEqual(format_number(0.00123456789, significant_figures=4), '1.235E-3')
        self.assertEqual(format_number(0.00123456789, significant_figures=5), '1.2346E-3')
        self.assertEqual(format_number(0.00123456789, significant_figures=6), '1.23457E-3')
        self.assertEqual(format_number(0.00123456789, significant_figures=7), '1.234568E-3')
        self.assertEqual(format_number(-0.00123456789, significant_figures=8), '-1.2345679E-3')
        self.assertEqual(format_number(-0.00123456789, significant_figures=9), '-1.23456789E-3')
        self.assertEqual(format_number(-0.00123456789, significant_figures=10), '-1.234567890E-3')

        self.assertEqual(format_number(1000, significant_figures=1, scientific_exponent_threshold=1), '1E+3')
        self.assertEqual(format_number(100, significant_figures=1, scientific_exponent_threshold=1), '1E+2')
        self.assertEqual(format_number(10, significant_figures=1, scientific_exponent_threshold=1), '1E+1')
        self.assertEqual(format_number(1, significant_figures=1, scientific_exponent_threshold=1), '1')
        self.assertEqual(format_number(0.1, significant_figures=1, scientific_exponent_threshold=1), '1E-1')
        self.assertEqual(format_number(0.01, significant_figures=1, scientific_exponent_threshold=1), '1E-2')
        self.assertEqual(format_number(0.001, significant_figures=1, scientific_exponent_threshold=1), '1E-3')

        self.assertEqual(format_number(1000, significant_figures=2, scientific_exponent_threshold=2), '1.0E+3')
        self.assertEqual(format_number(100, significant_figures=2, scientific_exponent_threshold=2), '1.0E+2')
        self.assertEqual(format_number(10, significant_figures=2, scientific_exponent_threshold=2), '10')
        self.assertEqual(format_number(1, significant_figures=2, scientific_exponent_threshold=2), '1.0')
        self.assertEqual(format_number(0.1, significant_figures=2, scientific_exponent_threshold=2), '0.10')
        self.assertEqual(format_number(0.01, significant_figures=2, scientific_exponent_threshold=2), '1.0E-2')
        self.assertEqual(format_number(0.001, significant_figures=2, scientific_exponent_threshold=2), '1.0E-3')

        self.assertEqual(format_number(1000, significant_figures=2, scientific_exponent_threshold=3), '1.0E+3')
        self.assertEqual(format_number(100, significant_figures=2, scientific_exponent_threshold=3), '1.0E+2')
        self.assertEqual(format_number(10, significant_figures=2, scientific_exponent_threshold=3), '10')
        self.assertEqual(format_number(1, significant_figures=2, scientific_exponent_threshold=3), '1.0')
        self.assertEqual(format_number(0.1, significant_figures=2, scientific_exponent_threshold=3), '0.10')
        self.assertEqual(format_number(0.01, significant_figures=2, scientific_exponent_threshold=3), '0.010')
        self.assertEqual(format_number(0.001, significant_figures=2, scientific_exponent_threshold=3), '1.0E-3')

        self.assertEqual(format_number(9.87654, significant_figures=1, scientific_exponent_threshold=0), '1E+1')
        self.assertEqual(format_number(9.87654, significant_figures=2, scientific_exponent_threshold=0), '9.9E+0')
        self.assertEqual(format_number(9.87654, significant_figures=3, scientific_exponent_threshold=0), '9.88E+0')
        self.assertEqual(format_number(9.87654, significant_figures=1, scientific_exponent_threshold=1), '1E+1')
        self.assertEqual(format_number(9.87654, significant_figures=2, scientific_exponent_threshold=1), '9.9')
        self.assertEqual(format_number(9.87654, significant_figures=3, scientific_exponent_threshold=1), '9.88')

        self.assertEqual(format_number(0.00999, significant_figures=1, scientific_exponent_threshold=2), '1E-2')
        self.assertEqual(format_number(0.00999, significant_figures=2, scientific_exponent_threshold=2), '1.0E-2')
        self.assertEqual(format_number(0.00999, significant_figures=3, scientific_exponent_threshold=2), '9.99E-3')
        self.assertEqual(format_number(0.00999, significant_figures=1, scientific_exponent_threshold=3), '0.01')
        self.assertEqual(format_number(0.00999, significant_figures=2, scientific_exponent_threshold=3), '0.010')
        self.assertEqual(format_number(0.00999, significant_figures=3, scientific_exponent_threshold=3), '9.99E-3')
        self.assertEqual(format_number(0.00999, significant_figures=1, scientific_exponent_threshold=4), '0.01')
        self.assertEqual(format_number(0.00999, significant_figures=2, scientific_exponent_threshold=4), '0.010')
        self.assertEqual(format_number(0.00999, significant_figures=3, scientific_exponent_threshold=4), '0.00999')
        self.assertEqual(format_number(0.00999, significant_figures=1, scientific_exponent_threshold=5), '0.01')
        self.assertEqual(format_number(0.00999, significant_figures=2, scientific_exponent_threshold=5), '0.010')
        self.assertEqual(format_number(0.00999, significant_figures=3, scientific_exponent_threshold=5), '0.00999')

    def test_descending_product(self):
        factors_1 = [0.1, 0.3, 0.5, 0.823]
        factors_2 = [0.823, 0.5, 0.3, 0.1]
        self.assertEqual(set(factors_1), set(factors_2))
        self.assertNotEqual(math.prod(factors_1), math.prod(factors_2))
        self.assertEqual(descending_product(factors_1), descending_product(factors_2))

    def test_descending_sum(self):
        terms_1 = [1e-9, 2.5e-12, 5e-13, 5e-10, 2.5e-12]
        terms_2 = [1e-9, 5e-10, 2.5e-12, 2.5e-12, 5e-13]
        self.assertEqual(set(terms_1), set(terms_2))
        self.assertNotEqual(sum(terms_1), sum(terms_2))
        self.assertEqual(descending_sum(terms_1), descending_sum(terms_2))

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
