"""
# Public Fault Tree Analyser: common.py

Commonly used convenience methods.

**Copyright 2025 Conway.**
Licensed under the GNU General Public License v3.0 (GPL-3.0-only).
This is free software with NO WARRANTY etc. etc., see LICENSE.
"""

from typing import Iterable, Optional, Union


def none_aware_dict_eq(self, other):
    if other is None:
        return False

    return self.__dict__ == other.__dict__


def natural_repr(self):
    class_name = type(self).__name__
    argument_sequence = ', '.join(f'{key}={value!r}' for key, value in self.__dict__.items())
    return f'{class_name}({argument_sequence})'


def natural_join(items: Union[tuple, list], penultimate_separator: Optional[str] = 'and') -> str:
    if not items:
        return ''

    if not penultimate_separator:
        return ', '.join(str(item) for item in items)

    length = len(items)

    if length == 1:
        return str(items[0])

    if length == 2:
        return f'{items[0]} {penultimate_separator} {items[1]}'

    leading_items_joined = ', '.join(str(item) for item in items[:-1])
    last_item = items[-1]
    return f'{leading_items_joined}, {penultimate_separator} {last_item}'


def natural_join_backticks(items: Union[tuple, list], penultimate_separator: Optional[str] = 'and') -> str:
    return natural_join([f'`{item}`' for item in items], penultimate_separator)


def format_cut_set(event_ids: tuple[str, ...]) -> str:
    if not event_ids:
        return 'True'

    return '.'.join(event_ids)


def format_quantity(value: Union[float, str], unit: str, is_reciprocal=False) -> str:
    if not unit:
        return value

    separator = '/' if is_reciprocal else ' '

    return f'{value}{separator}{unit}'
