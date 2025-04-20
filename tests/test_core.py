"""
# Public Fault Tree Analyser: test_core.py

Unit testing for `core.py`.

**Copyright 2025 Conway.**
Licensed under the GNU General Public License v3.0 (GPL-3.0-only).
This is free software with NO WARRANTY etc. etc., see LICENSE.
"""

import textwrap
import unittest

from pfta.core import FaultTree
from pfta.parsing import DuplicateIdException, UnsetPropertyException, NonPositiveTimeException


class TestCore(unittest.TestCase):
    def test_fault_tree(self):
        # Duplicate identifier
        self.assertRaises(
            DuplicateIdException,
            FaultTree,
            textwrap.dedent('''
                - time: 1

                Event: EV-001

                Event: EV-001
            '''),
        )

        # Unset time
        self.assertRaises(
            UnsetPropertyException,
            FaultTree,
            '- time_unit: h',
        )

        # Non-positive time
        self.assertRaises(
            NonPositiveTimeException,
            FaultTree,
            '- time: 0.',
        )
        self.assertRaises(
            NonPositiveTimeException,
            FaultTree,
            '- time: -1',
        )
        self.assertRaises(
            NonPositiveTimeException,
            FaultTree,
            '- time: 3, 4, -5',
        )
