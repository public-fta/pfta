"""
# Public Fault Tree Analyser: common.py

Commonly used convenience methods.

**Copyright 2025 Conway.**
Licensed under the GNU General Public License v3.0 (GPL-3.0-only).
This is free software with NO WARRANTY etc. etc., see LICENSE.
"""

from typing import Optional, Union, Sequence, TypeVar

T = TypeVar('T')


def none_aware_dict_eq(self: T, other: T) -> bool:
    if other is None:
        return False

    return self.__dict__ == other.__dict__


def natural_repr(self: T, omitted_attributes: tuple[str, ...] = tuple(),
                 ellipsis_attributes: tuple[str, ...] = tuple(), omit_private: bool = True) -> str:
    class_name = type(self).__name__
    argument_sequence = ', '.join(
        f'{attribute}={"<...>" if attribute in ellipsis_attributes else f"{value!r}"}'
        for attribute, value in self.__dict__.items()
        if attribute not in omitted_attributes
        if not (omit_private and attribute.startswith('_'))
    )

    return f'{class_name}({argument_sequence})'


def natural_join(items: Sequence[T], penultimate_separator: Optional[str] = 'and') -> str:
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


def natural_join_backticks(items: Sequence[T], penultimate_separator: Optional[str] = 'and') -> str:
    return natural_join([f'`{item}`' for item in items], penultimate_separator)


def format_cut_set(event_ids: tuple[str, ...]) -> str:
    if not event_ids:
        return 'True'

    return '.'.join(event_ids)


def format_quantity(value: Union[float, str], unit: str, is_reciprocal: bool = False) -> str:
    if not unit:
        return str(value)

    separator = '/' if is_reciprocal else ' '

    return f'{value}{separator}{unit}'
