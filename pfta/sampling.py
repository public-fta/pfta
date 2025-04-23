"""
# Public Fault Tree Analyser: sampling.py

Distribution sampling (i.e. pseudo-random number generation).

**Copyright 2025 Conway.**
Licensed under the GNU General Public License v3.0 (GPL-3.0-only).
This is free software with NO WARRANTY etc. etc., see LICENSE.
"""

import random

from pfta.common import natural_repr


class Distribution:
    def generate_samples(self, count: int) -> list[float]:
        raise NotImplementedError

    def __repr__(self):
        return natural_repr(self)


class DeltaDistribution(Distribution):
    def __init__(self, value: float):
        self.value = value

    def generate_samples(self, count: int) -> list[float]:
        return [self.value for _ in range(count)]


class LogNormalDistribution(Distribution):
    def __init__(self, mu: float, sigma: float):
        self.mu = mu
        self.sigma = sigma

    def generate_samples(self, count: int) -> list[float]:
        mu = self.mu
        sigma = self.sigma

        return [random.lognormvariate(mu, sigma) for _ in range(count)]


class NormalDistribution(Distribution):
    def __init__(self, mu: float, sigma: float):
        self.mu = mu
        self.sigma = sigma

    def generate_samples(self, count: int) -> list[float]:
        mu = self.mu
        sigma = self.sigma

        return [random.normalvariate(mu, sigma) for _ in range(count)]


class TriangularDistribution(Distribution):
    def __init__(self, lower: float, upper: float, mode: float):
        self.lower = lower
        self.upper = upper
        self.mode = mode

    def generate_samples(self, count: int) -> list[float]:
        low = self.lower
        high = self.upper
        mode = self.mode

        return [random.triangular(low, high, mode) for _ in range(count)]


class UniformDistribution(Distribution):
    def __init__(self, lower: float, upper: float):
        self.lower = lower
        self.upper = upper

    def generate_samples(self, count: int) -> list[float]:
        a = self.lower
        b = self.upper

        return [random.uniform(a, b) for _ in range(count)]
