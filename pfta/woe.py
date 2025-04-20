"""
# Public Fault Tree Analyser: woe.py

Ancestral classes indicative of woe.

**Copyright 2025 Conway.**
Licensed under the GNU General Public License v3.0 (GPL-3.0-only).
This is free software with NO WARRANTY etc. etc., see LICENSE.
"""


class FaultTreeTextException(Exception):
    def __init__(self, line_number: int | None, message: str, explainer: str = None):
        self.line_number = line_number
        self.message = message
        self.explainer = explainer


class ImplementationError(Exception):
    pass
