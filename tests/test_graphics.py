"""
# Public Fault Tree Analyser: test_graphics.py

Unit testing for `graphics.py`.

**Copyright 2025 Conway.**
Licensed under the GNU General Public License v3.0 (GPL-3.0-only).
This is free software with NO WARRANTY etc. etc., see LICENSE.
"""

import unittest

from pfta.graphics import escape_xml


class TestGraphics(unittest.TestCase):
    def test_escape_xml(self):
        self.assertEqual(escape_xml('&<>'), '&amp;&lt;&gt;')
        self.assertEqual(escape_xml('&amp;'), '&amp;')
        self.assertEqual(escape_xml('&lt;'), '&lt;')
        self.assertEqual(escape_xml('&gt;'), '&gt;')
        self.assertEqual(escape_xml('&&amp;'), '&amp;&amp;')
        self.assertEqual(escape_xml('&#1234567;'), '&#1234567;')
        self.assertEqual(escape_xml('&#12345678;'), '&amp;#12345678;')
        self.assertEqual(escape_xml('&#xABC123;'), '&#xABC123;')
        self.assertEqual(escape_xml('&#xABC123F;'), '&amp;#xABC123F;')
