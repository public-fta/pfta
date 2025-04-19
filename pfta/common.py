"""
# Public Fault Tree Analyser: common.py

Commonly used convenience methods.

**Copyright 2025 Conway.**
Licensed under the GNU General Public License v3.0 (GPL-3.0-only).
This is free software with NO WARRANTY etc. etc., see LICENSE.
"""


def convenient_eq(self, other):
    if other is None:
        return False

    return self.__dict__ == other.__dict__


def convenient_repr(self):
    class_name = type(self).__name__
    argument_sequence = ', '.join(f'{key}={value!r}' for key, value in self.__dict__.items())
    return f'{class_name}({argument_sequence})'
