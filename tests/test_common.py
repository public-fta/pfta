"""
# Public Fault Tree Analyser: test_common.py

Unit testing for `common.py`.

**Copyright 2025 Conway.**
Licensed under the GNU General Public License v3.0 (GPL-3.0-only).
This is free software with NO WARRANTY etc. etc., see LICENSE.
"""

import unittest

from pfta.common import natural_join, natural_join_backticks


class TestCommon(unittest.TestCase):
    def test_natural_join(self):
        self.assertEqual(natural_join([]), '')

        self.assertEqual(natural_join([1]), '1')
        self.assertEqual(natural_join(['one']), 'one')

        self.assertEqual(natural_join([1, 2]), '1 and 2')
        self.assertEqual(natural_join(['one', 'two']), 'one and two')

        self.assertEqual(natural_join([1, 2, 3]), '1, 2, and 3')
        self.assertEqual(natural_join(['one', 'two', 'three']), 'one, two, and three')

        self.assertEqual(
            natural_join([1, 2, 3, 4, 5, 6, 7, 8, 9]),
            '1, 2, 3, 4, 5, 6, 7, 8, and 9',
        )
        self.assertEqual(
            natural_join(['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']),
            'one, two, three, four, five, six, seven, eight, and nine',
        )

    def test_natural_join_backticks(self):
        self.assertEqual(natural_join_backticks([]), '')

        self.assertEqual(natural_join_backticks([1]), '`1`')
        self.assertEqual(natural_join_backticks(['one']), '`one`')

        self.assertEqual(natural_join_backticks([1, 2]), '`1` and `2`')
        self.assertEqual(natural_join_backticks(['one', 'two']), '`one` and `two`')

        self.assertEqual(natural_join_backticks([1, 2, 3]), '`1`, `2`, and `3`')
        self.assertEqual(natural_join_backticks(['one', 'two', 'three']), '`one`, `two`, and `three`')

        self.assertEqual(
            natural_join_backticks([1, 2, 3, 4, 5, 6, 7, 8, 9]),
            '`1`, `2`, `3`, `4`, `5`, `6`, `7`, `8`, and `9`',
        )
        self.assertEqual(
            natural_join_backticks(['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']),
            '`one`, `two`, `three`, `four`, `five`, `six`, `seven`, `eight`, and `nine`',
        )
