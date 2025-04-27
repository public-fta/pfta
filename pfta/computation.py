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

if typing.TYPE_CHECKING:
    from pfta.core import Event


class ComputationalCache:
    def __init__(self, events: list['Event']):
        probability_from_index_from_term = {
            event.computed_expression.sole_term(): dict(enumerate(event.computed_probabilities))
            for event in events
        }
        intensity_from_index_from_term = {
            event.computed_expression.sole_term(): dict(enumerate(event.computed_intensities))
            for event in events
        }

        self.probability_from_index_from_term = collections.defaultdict(dict, probability_from_index_from_term)
        self.intensity_from_index_from_term = collections.defaultdict(dict, intensity_from_index_from_term)

    def __repr__(self):
        return natural_repr(self)

    def probability(self, term, index) -> float:
        """
        Instantaneous failure probability of a Boolean term (minimal cut set).

        From `MATHS.md`, the failure product of a minimal cut set `C = x y z ...` is given by
            q[C] = q[x] q[y] q[z] ...,
        a straight product of the failure probabilities of its constituent primary events (i.e. factors).
        """
        if index not in self.probability_from_index_from_term[term]:
            probability = math.prod(  # TODO: replace with descending product
                self.probability_from_index_from_term[factor][index]
                for factor in term.factors()
            )
            self.probability_from_index_from_term[term][index] = probability

        return self.probability_from_index_from_term[term][index]


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
    TODO: For performance, we truncate after the latest term divided by the partial sum falls below a threshold.
    """
    term_count = len(terms)
    partial_sum = 0

    for order in range(1, term_count + 1):
        term_combos = itertools.combinations(terms, order)
        latest_term = sum(
            computational_cache.probability(Term.conjunction(*terms), flattened_index)
            for terms in term_combos
        )

        # TODO: threshold logic to break loop

        partial_sum += latest_term

    return partial_sum
