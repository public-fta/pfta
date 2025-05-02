"""
# Public Fault Tree Analyser: utilities.py

Mathematical utility methods.

**Copyright 2025 Conway.**
Licensed under the GNU General Public License v3.0 (GPL-3.0-only).
This is free software with NO WARRANTY etc. etc., see LICENSE.
"""

import math
from typing import Iterable


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
