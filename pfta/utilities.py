"""
# Public Fault Tree Analyser: utilities.py

Mathematical utility methods.

**Copyright 2025 Conway.**
Licensed under the GNU General Public License v3.0 (GPL-3.0-only).
This is free software with NO WARRANTY etc. etc., see LICENSE.
"""

import itertools
import math
import re
from typing import Iterable, Optional, Collection, TypeVar

from pfta.woe import ImplementationError

T = TypeVar('T')


def robust_divide(x: float, y: float) -> float:
    try:
        return x / y
    except ZeroDivisionError:
        return x * float('inf')


def robust_invert(x: float) -> float:
    try:
        return 1 / x
    except ZeroDivisionError:
        return float('inf')


def format_number(number: Optional[float],
                  decimal_places: Optional[int] = None, significant_figures: Optional[int] = None,
                  scientific_exponent_threshold: int = 3, simple_zero: bool = True) -> Optional[str]:
    if number is None:
        return None

    if not math.isfinite(number):
        return str(number)

    is_decimal_places_set = decimal_places is not None
    is_significant_figures_set = significant_figures is not None

    if is_decimal_places_set and is_significant_figures_set:
        raise ValueError('both decimal_places and significant_figures have been set')

    if not is_decimal_places_set and not is_significant_figures_set:
        raise ValueError('neither decimal_places nor significant_figures has been set')

    if simple_zero and number == 0:
        return '0'

    if is_decimal_places_set:
        if decimal_places < 0:
            raise ValueError('decimal_places must be non-negative')

        return f'{number:.{decimal_places}f}'

    if is_significant_figures_set:
        if significant_figures <= 0:
            raise ValueError('significant_figures must be positive')

        scientific_form = f'{number:.{significant_figures - 1}E}'

        scientific_match = re.fullmatch(
            '(?P<sign>-?)(?P<mantissa>[0-9.]+)E(?P<exponent_sign>[+-])0*(?P<exponent_magnitude>[0-9]+)',
            scientific_form,
        )

        if not scientific_match:
            raise ImplementationError('scientific_form did not match regex')

        sign_prefix = scientific_match.group('sign')
        mantissa = scientific_match.group('mantissa')
        exponent_sign = scientific_match.group('exponent_sign')
        exponent_magnitude = scientific_match.group('exponent_magnitude')  # without leading zeroes

        mantissa_digits = mantissa.replace('.', '')
        exponent = int(f'{exponent_sign}{exponent_magnitude}')

        force_scientific = abs(exponent) >= scientific_exponent_threshold
        insufficient_digits_for_unscientific = mantissa_digits[0] != 0 and len(mantissa_digits) - 1 < exponent

        if force_scientific or insufficient_digits_for_unscientific:
            return f'{sign_prefix}{mantissa}E{exponent_sign}{exponent_magnitude}'

        if exponent >= 0:
            integer_digits = mantissa_digits[0:exponent + 1]
            fractional_digits = mantissa_digits[exponent + 1:]

            magnitude_head = integer_digits if integer_digits else ''
            magnitude_trailing = f'.{fractional_digits}' if fractional_digits else ''

            return f'{sign_prefix}{magnitude_head}{magnitude_trailing}'

        else:
            fractional_leading_zeroes = (-exponent - 1) * '0'

            return f'{sign_prefix}0.{fractional_leading_zeroes}{mantissa_digits}'

    raise ImplementationError('bad argument logic')


def descending_product(factors: Iterable[float]) -> float:
    """
    Compute a product after sorting the factors in descending order.

    Needed to prevent cut set quantity computations from depending on event declaration order,
    due to the nature of floating-point arithmetic:
        0.1 * 0.3 * 0.5 * 0.823 = 0.012344999999999998
        0.823 * 0.5 * 0.3 * 0.1 = 0.012345
    """
    return math.prod(sorted(factors, reverse=True))


def descending_sum(terms: Iterable[float]) -> float:
    """
    Compute a sum after sorting the terms in descending order.

    Needed to prevent cut set quantity computations from depending on event declaration order,
    due to the nature of floating-point arithmetic:
        1e-9 + 2.5e-12 + 5e-13 + 5e-10 + 2.5e-12 = 1.5054999999999998e-09
        1e-9 + 5e-10 + 2.5e-12 + 2.5e-12 + 5e-13 = 1.5055e-09
    """
    return sum(sorted(terms, reverse=True))


def concrete_combinations(items: Collection[T], order: int) -> list[tuple[T, ...]]:
    """
    Compute concrete term combinations (subset-tuples) of given order (size).

    Concrete, because `itertools.combinations` returns an iterator (which gets consumed on first iteration),
    and we convert it to a list so that it persists multiple iterations.
    """
    return list(itertools.combinations(items, order))


def find_cycles(adjacency_dict: dict):
    """
    Find cycles of a directed graph via three-state (clean, infected, dead) depth-first search.
    """
    infection_cycles = set()
    infection_chain = []

    clean_nodes = set(adjacency_dict)
    infected_nodes = set()
    # dead_nodes need not be tracked

    def infect(node):
        clean_nodes.discard(node)
        infected_nodes.add(node)
        infection_chain.append(node)

        for child_node in sorted(adjacency_dict[node]):
            if child_node in infected_nodes:  # cycle discovered
                child_index = infection_chain.index(child_node)
                infection_cycles.add(tuple(infection_chain[child_index:]))

            elif child_node in clean_nodes:  # clean child to be infected
                infect(child_node)

        infected_nodes.discard(node)  # infected node dies
        infection_chain.pop()

    while clean_nodes:
        first_clean_node = min(clean_nodes)
        infect(first_clean_node)

    return infection_cycles
