"""
# Public Fault Tree Analyser: core.py

Core fault tree analysis classes.

**Copyright 2025 Conway**
Licensed under the GNU General Public License v3.0 (GPL-3.0-only).
This is free software with NO WARRANTY etc. etc., see LICENSE.
"""

from pfta.parser import parse


class FaultTree:
    def __init__(self, fault_tree_text: str):
        parse(fault_tree_text)
