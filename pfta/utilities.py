"""
# Public Fault Tree Analyser: utilities.py

Mathematical utility methods.

**Copyright 2025 Conway.**
Licensed under the GNU General Public License v3.0 (GPL-3.0-only).
This is free software with NO WARRANTY etc. etc., see LICENSE.
"""

import decimal
import math
from typing import Iterable, Optional

from pfta.woe import ImplementationError


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
                  force_scientific_exponent: int = 3, return_plain_zero: bool = True) -> Optional[str]:
    if number is None:
        return None

    if not math.isfinite(number):
        return str(number)

    if return_plain_zero and number == 0:
        return '0'

    is_decimal_places_set = decimal_places is not None
    is_significant_figures_set = significant_figures is not None

    if is_decimal_places_set and is_significant_figures_set:
        raise ValueError('both decimal_places and significant_figures have been set')

    if not is_decimal_places_set and not is_significant_figures_set:
        raise ValueError('neither decimal_places nor significant_figures has been set')

    decimal_value = decimal.Decimal(number)

    if is_decimal_places_set:
        return str(round(decimal_value, ndigits=decimal_places))

    if is_significant_figures_set:
        exponent = decimal_value.adjusted()
        critical_place = exponent - (significant_figures - 1)
        decimal_rounded = round(decimal_value, ndigits=-critical_place)

        if abs(exponent) < force_scientific_exponent:
            return str(decimal_rounded)
        else:
            sign_power, mantissa_digits, _ = decimal_rounded.as_tuple()

            sign_symbol = '-' if sign_power == 1 else ''
            leading_digit = mantissa_digits[0]
            trailing_digits = ''.join(str(digit) for digit in mantissa_digits[1:])
            decimal_point = '.' if trailing_digits else ''

            return f'{sign_symbol}{leading_digit}{decimal_point}{trailing_digits}E{exponent:+d}'

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
