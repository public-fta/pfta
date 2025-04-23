"""
# Public Fault Tree Analyser: common.py

Commonly used convenience methods.

**Copyright 2025 Conway.**
Licensed under the GNU General Public License v3.0 (GPL-3.0-only).
This is free software with NO WARRANTY etc. etc., see LICENSE.
"""

from typing import Iterable


def none_aware_dict_eq(self, other):
    if other is None:
        return False

    return self.__dict__ == other.__dict__


def natural_repr(self):
    class_name = type(self).__name__
    argument_sequence = ', '.join(f'{key}={value!r}' for key, value in self.__dict__.items())
    return f'{class_name}({argument_sequence})'


def natural_join(items: tuple | list, penultimate_separator: str | None = 'and') -> str:
    if not items:
        return ''

    if not penultimate_separator:
        return ', '.join(str(item) for item in items)

    length = len(items)

    if length == 1:
        return str(items[0])

    if length == 2:
        return f'{items[0]} {penultimate_separator} {items[1]}'

    joined_to_penultimate = ', '.join(str(item) for item in items[0:-1])
    return f'{joined_to_penultimate}, {penultimate_separator} {items[-1]}'


def natural_join_backticks(items: tuple | list, penultimate_separator: str | None = 'and') -> str:
    return natural_join([f'`{item}`' for item in items], penultimate_separator)


def format_cut_set(event_ids: Iterable[str]):
    return '.'.join(event_ids)
