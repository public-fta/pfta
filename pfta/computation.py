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
import typing

from pfta.boolean import Term
from pfta.common import natural_repr
from pfta.utilities import robust_divide, descending_product, descending_sum

if typing.TYPE_CHECKING:
    from pfta.core import Event


class ComputationalCache:
    def __init__(self, tolerance: float, events: list['Event']):
        probability_from_index_from_term = {
            event.computed_expression.sole_term(): dict(enumerate(event.computed_probabilities))
            for event in events
        }
        intensity_from_index_from_term = {
            event.computed_expression.sole_term(): dict(enumerate(event.computed_intensities))
            for event in events
        }

        self.tolerance = tolerance
        self._probability_from_index_from_term = collections.defaultdict(dict, probability_from_index_from_term)
        self._intensity_from_index_from_term = collections.defaultdict(dict, intensity_from_index_from_term)

    def __repr__(self):
        return natural_repr(self)

    def probability(self, term, index) -> float:
        """
        Instantaneous failure probability of a Boolean term (minimal cut set).

        From `MATHS.md`, the failure probability of a minimal cut set `C = x y z ...` is given by
            q[C] = q[x] q[y] q[z] ...
                 = ∏{e|C} q[C],
        a straight product of the failure probabilities of its constituent primary events (i.e. factors).
        """
        if index not in self._probability_from_index_from_term[term]:
            def q(e: Term) -> float:
                return self.probability(e, index)

            probability = descending_product(q(factor) for factor in term.factors())

            self._probability_from_index_from_term[term][index] = probability

        return self._probability_from_index_from_term[term][index]

    def intensity(self, term, index) -> float:
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
        if index not in self._intensity_from_index_from_term[term]:
            def q(e: Term) -> float:
                return self.probability(e, index)

            def omega(e: Term) -> float:
                return self.intensity(e, index)

            intensity = descending_sum(omega(factor) * q(term / factor) for factor in term.factors())

            self._intensity_from_index_from_term[term][index] = intensity

        return self._intensity_from_index_from_term[term][index]

    def rate(self, term, index) -> float:
        """
        Instantaneous failure rate of a Boolean term (minimal cut set).
        """
        q = self.probability(term, index)
        omega = self.intensity(term, index)

        return omega / (1 - q)


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


def disjunction_probability(terms: list[Term], flattened_index: int, computational_cache: ComputationalCache) -> float:
    """
    Instantaneous failure probability of a disjunction (OR) of a list of Boolean terms (minimal cut sets).

    From `MATHS.md`, for a gate `T` represented as a disjunction of `N` minimal cut sets,
        T = C_1 + C_2 + ... + C_N,
    the failure probability `q[T]` of the top gate is given by the inclusion–exclusion principle,
        q[T] =   ∑{1≤i≤N} q[C_i]
               − ∑{1≤i<j≤N} q[C_i C_j]
               + ∑{1≤i<j<k≤N} q[C_i C_j C_k]
               − ... .
    For performance, we truncate after the latest term divided by the partial sum falls below the tolerance.
    """
    term_count = len(terms)
    partial_sum = 0

    def q(term: Term) -> float:
        return computational_cache.probability(term, flattened_index)

    and_ = Term.conjunction

    for order in range(1, term_count + 1):
        combos = itertools.combinations(terms, order)

        latest_term = (-1)**(order - 1) * sum(q(and_(*combo)) for combo in combos)

        partial_sum += latest_term

        if latest_term == 0 or abs(robust_divide(latest_term, partial_sum)) < computational_cache.tolerance:
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
        ω^2[T] =   ∑{1≤i≤N} ω_r[{C_i}]
                 − ∑{1≤i<j≤N} ω_r[{C_i,C_j}]
                 + ... ,
        ω_r[{C_i,C_j,...}]
               =   ∑{1≤a≤N} ω[gcd(C_i,C_j,...) ÷ (C_a)] q[(C_a) (C_i C_j ...) ÷ gcd(C_i,C_j,...)]
                 − ∑{1≤a<b≤N} ω[gcd(C_i,C_j,...) ÷ (C_a C_b)] q[(C_a C_b) (C_i C_j ...) ÷ gcd(C_i,C_j,...)]
                 + ... .
    For performance, we truncate after the latest `ω^1 + ω^2` term divided by the partial sum falls below the tolerance.
    """
    term_count = len(terms)
    partial_sum = 0

    def q(term: Term) -> float:
        return computational_cache.probability(term, flattened_index)

    def omega(term: Term) -> float:
        return computational_cache.intensity(term, flattened_index)

    def omega_r(combo: tuple[Term, ...]) -> float:
        return redundant_intensity_mini_term(combo, terms, flattened_index, computational_cache)

    gcd = Term.gcd
    and_ = Term.conjunction

    for order in range(1, term_count + 1):
        combos = itertools.combinations(terms, order)

        latest_omega_1_term = (
            (-1)**(order - 1) * sum(omega(gcd(*combo)) * q(and_(*combo) / gcd(*combo)) for combo in combos)
        )
        latest_omega_2_term = (
            (-1)**(order - 1) * sum(omega_r(combo) for combo in combos)
        )
        latest_term = latest_omega_1_term + latest_omega_2_term

        partial_sum += latest_term

        if latest_term == 0 or abs(robust_divide(latest_term, partial_sum)) < computational_cache.tolerance:
            break

    return partial_sum


def redundant_intensity_mini_term(terms_subset: tuple[Term, ...], terms: list[Term], flattened_index: int,
                                  computational_cache: ComputationalCache) -> float:
    """
    Contributing mini-term `ω_r[{C_i,C_j,...}]` in the redundant contribution `ω^2[T]` to failure intensity.

    This is the redundant contribution to the failure intensity of `T = C_1 + C_2 + ... + C_N`
    from the combinational subset `{C_i,C_j,...}` of terms already being failed.

    From `MATHS.md`,
        ω_r[{C_i,C_j,...}]
               =   ∑{1≤a≤N} ω[gcd(C_i,C_j,...) ÷ (C_a)] q[(C_a) (C_i C_j ...) ÷ gcd(C_i,C_j,...)]
                 − ∑{1≤a<b≤N} ω[gcd(C_i,C_j,...) ÷ (C_a C_b)] q[(C_a C_b) (C_i C_j ...) ÷ gcd(C_i,C_j,...)]
                 + ... .
    """
    term_count = len(terms)
    partial_sum = 0

    def q(term: Term) -> float:
        return computational_cache.probability(term, flattened_index)

    def omega(term: Term) -> float:
        return computational_cache.intensity(term, flattened_index)

    gcd = Term.gcd
    and_ = Term.conjunction

    for order in range(1, term_count + 1):
        combos = itertools.combinations(terms, order)

        latest_term = (
            (-1)**(order - 1)
            * sum(
                omega(gcd(*terms_subset) / and_(*combo)) * q(and_(*combo, *terms_subset) / gcd(*terms_subset))
                for combo in combos
            )
        )

        partial_sum += latest_term

    return partial_sum
