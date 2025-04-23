"""
# Public Fault Tree Analyser: sampling.py

Distribution sampling (i.e. pseudo-random number generation).

**Copyright 2025 Conway.**
Licensed under the GNU General Public License v3.0 (GPL-3.0-only).
This is free software with NO WARRANTY etc. etc., see LICENSE.
"""


class Distribution:
    def generate_samples(self, count: int) -> list[float]:
        raise NotImplementedError


class ConstantDistribution(Distribution):
    def __init__(self, value: float):
        self.value = value

    def generate_samples(self, count: int) -> list[float]:
        return [self.value for _ in range(count)]
