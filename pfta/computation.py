"""
# Public Fault Tree Analyser: computation.py

Fault tree computational methods.

**Copyright 2025 Conway.**
Licensed under the GNU General Public License v3.0 (GPL-3.0-only).
This is free software with NO WARRANTY etc. etc., see LICENSE.
"""

import math


def constant_rate_model_probability(t: float, lambda_: float, mu: float) -> float:
    """
    Instantaneous failure probability q(t) for a component with constant failure and repair rates λ and μ.

    Explicitly, q(t) = [λ/(λ+μ)] [1 − exp(−(λ+μ)t)].

    - If λ = 0 and μ = 0 and t = inf | nan,    then q(t) = nan  (since [...] and [...] are independently indeterminate)
    - If λ = 0 and μ = 0 and t ≠ inf | nan,    then q(t) = 0    (from expanding in the small parameter (λ+μ)t)
    - If λ = 0 and μ ≠ 0,                      then q(t) = 0    (since [...] = 0 and 0 ≤ [...] ≤ 1)
    - If λ = inf and μ = inf | nan,            then q(t) = nan  (since [...] is indeterminate and 0 ≤ [...] ≤ 1)
    - If λ = inf and μ ≠ inf | nan and t = 0,  then q(t) = nan  (since [...] = 1 and [...] is indeterminate)
    - If λ = inf and μ ≠ inf | nan and t ≠ 0,  then q(t) = 1    (since [...] = 1 and [...] = 1)
    - If λ = nan,                              then q(t) = nan  (since [...] and [...] are independently indeterminate)
    - If λ ≠ 0 | inf | nan and μ = inf,        then q(t) = 0    (since [...] = 0 and 0 ≤ [...] ≤ 1)
    - If λ ≠ 0 | inf | nan and μ = nan,        then q(t) = nan  (since [...] and [...] are independently indeterminate)
    """
    if lambda_ == 0:
        if mu == 0 and (math.isinf(t) or math.isnan(t)):
            return float('nan')

        return 0.

    if math.isinf(lambda_):
        if not (math.isinf(mu) or math.isnan(mu)) and (t != 0):
            return 1.

        return float('nan')

    if math.isnan(lambda_):
        return float('nan')

    if math.isinf(mu):
        return 0.

    if math.isnan(mu):
        return float('nan')

    return lambda_ / (lambda_+mu) * -math.expm1(-(lambda_+mu) * t)
