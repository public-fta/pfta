"""
# Public Fault Tree Analyser: test_core.py

Unit testing for `core.py`.

**Copyright 2025 Conway.**
Licensed under the GNU General Public License v3.0 (GPL-3.0-only).
This is free software with NO WARRANTY etc. etc., see LICENSE.
"""

import unittest

from pfta.core import FaultTree
from pfta.parsing import UnsetPropertyException


class TestCore(unittest.TestCase):
    def test_fault_tree(self):
        # Unset time
        self.assertRaises(
            UnsetPropertyException,
            FaultTree,
            '- time_unit: h',
        )
