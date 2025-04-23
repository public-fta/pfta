"""
# Public Fault Tree Analyser: sampling.py

Distribution sampling (i.e. pseudo-random number generation).

**Copyright 2025 Conway.**
Licensed under the GNU General Public License v3.0 (GPL-3.0-only).
This is free software with NO WARRANTY etc. etc., see LICENSE.
"""

import random


class Distribution:
    def generate_samples(self, count: int) -> list[float]:
        raise NotImplementedError


class ConstantDistribution(Distribution):
    def __init__(self, value: float):
        self.value = value

    def generate_samples(self, count: int) -> list[float]:
        return [self.value for _ in range(count)]


class UniformDistribution(Distribution):
    def __init__(self, lower: float, upper: float):
        self.lower = lower
        self.upper = upper

    def generate_samples(self, count: int) -> list[float]:
        a = self.lower
        b = self.upper

        return [random.uniform(a, b) for _ in range(count)]
