"""
# Public Fault Tree Analyser: computation.py

Fault tree computational methods.

**Copyright 2025 Conway.**
Licensed under the GNU General Public License v3.0 (GPL-3.0-only).
This is free software with NO WARRANTY etc. etc., see LICENSE.
"""

import collections
import itertools
import math
from typing import TYPE_CHECKING, Collection, Iterable

from pfta.boolean import Term
from pfta.common import natural_repr
from pfta.utilities import robust_divide, descending_product, descending_sum

if TYPE_CHECKING:
    from pfta.core import Event


class ComputationalCache:
    def __init__(self, tolerance: float, events: list['Event']):
        probability_from_index_from_encoding = {
            event.computed_expression.sole_term().encoding: dict(enumerate(event.computed_probabilities))
            for event in events
        }
        intensity_from_index_from_encoding = {
            event.computed_expression.sole_term().encoding: dict(enumerate(event.computed_intensities))
            for event in events
        }

        self.tolerance = tolerance
        self._probability_from_index_from_encoding = collections.defaultdict(dict, probability_from_index_from_encoding)
        self._intensity_from_index_from_encoding = collections.defaultdict(dict, intensity_from_index_from_encoding)
        self._combinations_from_order_from_terms = collections.defaultdict(dict)

    def __repr__(self):
        return natural_repr(self)

    def probability(self, term: Term, index: int) -> float:
        """
        Instantaneous failure probability of a Boolean term (minimal cut set).

        From `MATHS.md`, the failure probability of a minimal cut set `C = x y z ...` is given by
            q[C] = q[x] q[y] q[z] ...
                 = ∏{e|C} q[C],
        a straight product of the failure probabilities of its constituent primary events (i.e. factors).
        """
        if index not in self._probability_from_index_from_encoding[term.encoding]:
            def q(e: Term) -> float:
                return self.probability(e, index)

            probability = descending_product(q(factor) for factor in term.factors())

            self._probability_from_index_from_encoding[term.encoding][index] = probability

        return self._probability_from_index_from_encoding[term.encoding][index]

    def intensity(self, term: Term, index: int) -> float:
        """
        Instantaneous failure intensity of a Boolean term (minimal cut set).

        From `MATHS.md`, the failure intensity of a minimal cut set `C = x y z ...`
        is given by a product-rule-style expression, where each term is the product of
        one primary event's failure intensity and the remaining primary events' failure probabilities:
            ω[C] =   ω[x] q[y] q[z] ...
                   + q[x] ω[y] q[z] ...
                   + q[x] q[y] ω[z] ...
                   + ...
                 = ∑{e|C} ω[e] q[C÷e].
        """
        if index not in self._intensity_from_index_from_encoding[term.encoding]:
            def q(e: Term) -> float:
                return self.probability(e, index)

            def omega(e: Term) -> float:
                return self.intensity(e, index)

            intensity = descending_sum(omega(factor) * q(term / factor) for factor in term.factors())

            self._intensity_from_index_from_encoding[term.encoding][index] = intensity

        return self._intensity_from_index_from_encoding[term.encoding][index]

    def rate(self, term: Term, index: int) -> float:
        """
        Instantaneous failure rate of a Boolean term (minimal cut set).
        """
        q = self.probability(term, index)
        omega = self.intensity(term, index)

        return robust_divide(omega, 1 - q)

    def combinations(self, terms: Collection[Term], order: int) -> list[tuple[Term, ...]]:
        """
        Term combinations (subset-tuples) of given order (size).
        """
        if order not in self._combinations_from_order_from_terms[terms]:
            combos = concrete_combinations(terms, order)

            self._combinations_from_order_from_terms[terms][order] = combos

        return self._combinations_from_order_from_terms[terms][order]


def constant_rate_model_probability(t: float, lambda_: float, mu: float) -> float:
    """
    Instantaneous failure probability q(t) for a component with constant failure and repair rates λ and μ.

    Explicitly, q(t) = [λ/(λ+μ)] [1−exp(−(λ+μ)t)].

    |  λ  |  μ  |  t  |  q  | Explanation
    | --- | --- | --- | --- | -----------
    |  0  |  0  | i|n | nan | 0/0 [1−exp(−0.i|n)] = nan (since 0/0 is independent of i|n)
    |     |     | oth |  0  | λ/(λ+μ).(λ+μ)t = λt = 0
    |     | inf | any |  0  | 0/i [1−exp(−i.any)] = 0.finite = 0
    |     | nan | i|n | nan | {nan (per above) if μ=0}
    |     |     | oth |  0  | {0 (per above) if μ=0; 0/μ [1−exp(−μt)] = 0.finite = 0 if μ≠0}  # mergeable with next
    |     | oth | any |  0  | 0/μ [1−exp(−μ.any)] = 0.finite = 0
    | inf | i|n | any | nan | i/(i+i|n) [1−exp(−(i+i|n).any)] = nan.finite = nan
    |     | oth | 0|n | nan | 1 [1−exp(−inf.0|n)] = 1.nan = nan
    |     |     | oth |  1  | 1 [1−exp(−inf.t)] = 1.1 = 1
    | nan |  0  | i|n | nan | {nan (per above) if λ=0}
    |     |     | oth | nan | 1 [1−exp(−nan.t)] = nan                                         # mergeable with previous
    |     | i|n | any | nan | {nan (per above) if λ=inf}                                      # mergeable with previous
    |     | oth | any | nan | nan [1−exp(−nan.any)] = nan.finite = nan                        # mergeable with previous
    | oth | inf | any |  0  | λ/i [1−exp(−i.any)] = 0.finite = 0
    |     | nan | inf | nan | {0 (per above) if μ=inf; 1 [1−exp(−λ.inf)] = 1 if μ=0}
    |     |     | oth | nan | {0 (per above) if μ=inf; 1 [1−exp(−λ.t)] ≠ 0 if μ=0}            # mergeable with previous
    |     | oth | any | :-) | computable
    """
    if lambda_ == 0:
        if mu == 0:
            if math.isinf(t) or math.isnan(t):
                return float('nan')

            return 0.

        if math.isinf(mu):
            return 0.

        if math.isnan(mu):
            if math.isinf(t) or math.isnan(t):
                return float('nan')

        return 0.

    if math.isinf(lambda_):
        if math.isinf(mu) or math.isnan(mu):
            return float('nan')

        if t == 0 or math.isnan(t):
            return float('nan')

        return 1.

    if math.isnan(lambda_):
        return float('nan')

    if math.isinf(mu):
        return 0.

    if math.isnan(mu):
        return float('nan')

    return lambda_ / (lambda_+mu) * -math.expm1(-(lambda_+mu) * t)


def constant_rate_model_intensity(t: float, lambda_: float, mu: float) -> float:
    """
    Instantaneous failure intensity ω(t) for a component with constant failure and repair rates λ and μ.

    Explicitly, ω(t) = λ (1−q(t)), where q(t) is the corresponding failure probability.

    |  λ  |  μ  |  t  |  ω  | Explanation
    | --- | --- | --- | --- | -----------
    |  0  | any | any |  0  | 0 (1−q(t)) = 0.finite = 0
    | inf | i|n | any | nan | {i (1−q(t)) = i.1 = i if λ/μ=0; λ (1−[1−exp(−λ.t)]) = 0 if λ/μ=inf}
    |     | oth | 0|n | nan | i . 1 [1−exp(−i.0|n)] = nan (since i is independent of 0|n)
    |     |     | oth |  μ  | λ (1−λ/(λ+μ).1) = λ μ/(λ+μ) = μ
    | nan | i|n | any | nan | {nan (per above) if λ=inf}
    |     | oth | 0|n | nan | {nan (per above) if λ=inf}                                      # mergeable with previous
    |     |     | oth | nan | {0 (per above) if λ=0; μ (per above) if λ=inf}                  # mergeable with previous
    | oth | inf | any |  λ  | λ (1−q(t)) = λ.(1−0) = λ
    |     | nan | any | nan | λ (1−q(t)) = λ.(1−nan) = nan
    |     | oth | any | :-) | computable
    """
    if lambda_ == 0:
        return 0.

    if math.isinf(lambda_):
        if math.isinf(mu) or math.isnan(mu):
            return float('nan')

        if t == 0 or math.isnan(t):
            return float('nan')

        return mu

    if math.isnan(lambda_):
        return float('nan')

    if math.isinf(mu):
        return lambda_

    if math.isnan(mu):
        return float('nan')

    q = constant_rate_model_probability(t, lambda_, mu)
    return lambda_ * (1 - q)


def concrete_combinations(terms: Collection[Term], order: int) -> list[tuple[Term, ...]]:
    """
    Compute concrete term combinations (subset-tuples) of given order (size).

    Concrete, because `itertools.combinations` returns an iterator (which gets consumed on first iteration),
    and we convert it to a list so that it persists multiple iterations.
    """
    return list(itertools.combinations(terms, order))


def should_terminate_sum(latest: float, partial_sum: float, tolerance: float) -> bool:
    """
    Predicate for early termination (truncation) of disjunction probability and intensity computations.
    """
    return math.isnan(latest) or latest == 0 or abs(latest) < abs(partial_sum) * tolerance


def disjunction_probability(terms: Collection[Term], flattened_index: int,
                            computational_cache: ComputationalCache) -> float:
    """
    Instantaneous failure probability of a disjunction (OR) of a list of Boolean terms (minimal cut sets).

    From `MATHS.md`, for a gate `T` represented as a disjunction of `N` minimal cut sets,
        T = C_1 + C_2 + ... + C_N,
    the failure probability `q[T]` of the top gate is given by the inclusion–exclusion principle,
        q[T] =   ∑{1≤i≤N} q[C_i]
               − ∑{1≤i<j≤N} q[C_i C_j]
               + ∑{1≤i<j<k≤N} q[C_i C_j C_k]
               − ... .
    In the implementation, we truncate after the latest contribution divided by the partial sum
    falls below the tolerance.
    """
    and_ = Term.conjunction
    combinations = computational_cache.combinations

    def q(term: Term) -> float:
        return computational_cache.probability(term, flattened_index)

    def q_contribution(order: int) -> float:
        return (
            (-1) ** (order - 1)
            * sum(
                q(and_(*combo))
                for combo in combinations(terms, order)
            )
        )

    partial_sum = 0

    for r in range(1, len(terms) + 1):
        latest = q_contribution(order=r)

        partial_sum += latest

        if should_terminate_sum(latest, partial_sum, computational_cache.tolerance):
            break

    return partial_sum


def disjunction_intensity(terms: list[Term], flattened_index: int, computational_cache: ComputationalCache) -> float:
    """
    Instantaneous failure intensity of a disjunction (OR) of a list of Boolean terms (minimal cut sets).

    From `MATHS.md`, for a gate `T` represented as a disjunction of `N` minimal cut sets,
        T = C_1 + C_2 + ... + C_N,
    the failure intensity `ω[T]` of the top gate is given by
        ω[T] = ω^1[T] − ω^2[T],
    where
        ω^1[T] =   ∑{1≤i≤N} ω[C_i]
                 − ∑{1≤i<j≤N} ω[gcd(C_i,C_j)] q[C_i C_j ÷ gcd(C_i,C_j)]
                 + ... ,
        ω^2[T] =   ∑{1≤i≤N} ω^†[C_i]
                 − ∑{1≤i<j≤N} ω^†[C_i,C_j]
                 + ... ,
        ω^†[C_i,C_j,...]
               =   ∑{1≤a≤N} ω[gcd(C_i,C_j,...) ÷ (C_a)] q[(C_a) (C_i C_j ... ÷ gcd(C_i,C_j,...))]
                 − ∑{1≤a<b≤N} ω[gcd(C_i,C_j,...) ÷ (C_a C_b)] q[(C_a C_b) (C_i C_j ... ÷ gcd(C_i,C_j,...))]
                 + ... .
    Successive upper, lower, upper, ... bounds may be obtained by computing
        (ω^1 truncated at 1st-order),
        (ω^1 truncated at 2nd-order) − (ω^2 truncated at 1st-order with ω^† truncated at 1st-order),
        (ω^1 truncated at 3rd-order) − (ω^2 truncated at 2nd-order with ω^† truncated at 2nd-order),
        (ω^1 truncated at 4th-order) − (ω^2 truncated at 3rd-order with ω^† truncated at 3rd-order),
        etc.
    To avoid unnecessary recomputation, we implement this by computing the successive contributions
        (ω^1 1st-order contribution),
        (ω^1 2nd-order contribution) − (ω^2 1st-order contribution with ω^† truncated at 1st-order),
        (ω^1 3rd-order contribution) − (ω^2 (1st)-order contribution's ω^† 2nd-order contribution
                                     − (ω^2 2nd-order contribution with ω^† truncated at 2nd-order),
        (ω^1 4th-order contribution) − (ω^2 (1st,2nd)-order contributions' ω^† 3rd-order contribution
                                     − (ω^2 3rd-order contribution with ω^† truncated at 3rd-order),
        etc.
    Thus, we truncate after the latest contribution
        (ω^1 rth-order contribution) − (ω^2 (1,...,r−2)th-order contributions' ω^† (r−1)th-order contribution)
                                     − (ω^2 (r−1)th-order contribution with ω^† truncated at (r−1)th-order)
    divided by the partial sum falls below the tolerance.
    """
    gcd = Term.gcd
    and_ = Term.conjunction
    combinations = computational_cache.combinations

    def q(term: Term) -> float:
        return computational_cache.probability(term, flattened_index)

    def omega(term: Term) -> float:
        return computational_cache.intensity(term, flattened_index)

    def omega_1_contribution(order: int) -> float:
        return (
            (-1) ** (order - 1)
            * sum(
                omega(combo_gcd) * q(and_(*combo) / combo_gcd)
                for combo in combinations(terms, order)
                if not (combo_gcd := gcd(*combo)).is_vacuous()  # skip q computation if omega is zero
            )
        )

    def omega_2_contribution(order: int, omega_dagger_orders: Iterable[int]) -> float:
        return (
            (-1) ** (order - 1)
            * sum(
                omega_dagger_contributions(combo, omega_dagger_orders)
                for combo in combinations(terms, order)
            )
        )

    def omega_dagger_contributions(combo: tuple[Term, ...], orders: Iterable[int]) -> float:
        return sum(
            omega_dagger_contribution(combo, order)
            for order in orders
        )

    def omega_dagger_contribution(combo: tuple[Term, ...], order: int) -> float:
        return (
            (-1) ** (order - 1)
            * sum(
                omega(combo_gcd_divided_by_failed) * q(and_(*failed, and_(*combo) / combo_gcd))
                for failed in combinations(terms, order)
                if not (combo_gcd := gcd(*combo)).is_vacuous()  # skip q computation if omega is zero
                if not (combo_gcd_divided_by_failed := combo_gcd / and_(*failed)).is_vacuous()  # ditto
            )
        )

    partial_sum = 0

    for r in range(1, len(terms) + 1):
        latest = (
            omega_1_contribution(order=r)
            - sum(
                omega_2_contribution(order=s, omega_dagger_orders=[r-1])
                for s in range(1, r-1)
            )
            - omega_2_contribution(order=r-1, omega_dagger_orders=range(1, r))
        )

        partial_sum += latest

        if should_terminate_sum(latest, partial_sum, computational_cache.tolerance):
            break

    return partial_sum
