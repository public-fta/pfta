"""
# Public Fault Tree Analyser: common.py

Commonly used convenience methods.

**Copyright 2025 Conway.**
Licensed under the GNU General Public License v3.0 (GPL-3.0-only).
This is free software with NO WARRANTY etc. etc., see LICENSE.
"""


def none_aware_dict_eq(self, other):
    if other is None:
        return False

    return self.__dict__ == other.__dict__


def natural_repr(self):
    class_name = type(self).__name__
    argument_sequence = ', '.join(f'{key}={value!r}' for key, value in self.__dict__.items())
    return f'{class_name}({argument_sequence})'


def natural_join(items: list) -> str:
    if not items:
        return ''

    length = len(items)

    if length == 1:
        return str(items[0])

    if length == 2:
        return f'{items[0]} and {items[1]}'

    joined_to_penultimate = ', '.join(str(item) for item in items[0:-1])
    return f'{joined_to_penultimate}, and {items[-1]}'
