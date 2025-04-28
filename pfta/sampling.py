"""
# Public Fault Tree Analyser: sampling.py

Distribution sampling (i.e. pseudo-random number generation).

**Copyright 2025 Conway.**
Licensed under the GNU General Public License v3.0 (GPL-3.0-only).
This is free software with NO WARRANTY etc. etc., see LICENSE.
"""

import math
import random

from pfta.common import natural_repr
from pfta.woe import FaultTreeTextException


class InvalidDistributionParameterException(FaultTreeTextException):
    pass


class Distribution:
    def __init__(self, line_number: int):
        self.line_number = line_number

    def __repr__(self):
        return natural_repr(self)

    def generate_samples(self, count: int) -> list[float]:
        raise NotImplementedError


class DegenerateDistribution(Distribution):
    def __init__(self, value: float, line_number: int):
        self.value = value
        super().__init__(line_number)

    def generate_samples(self, count: int) -> list[float]:
        return [self.value for _ in range(count)]


class LogNormalDistribution(Distribution):
    def __init__(self, mu: float, sigma: float, line_number: int):
        self.mu = mu
        self.sigma = sigma
        super().__init__(line_number)

    def generate_samples(self, count: int) -> list[float]:
        mu = self.mu
        sigma = self.sigma

        return [random.lognormvariate(mu, sigma) for _ in range(count)]


class LogUniformDistribution(Distribution):
    def __init__(self, lower: float, upper: float, line_number: int):
        if lower <= 0:
            raise InvalidDistributionParameterException(
                line_number,
                f'loguniform distribution parameter `lower={lower}` not positive',
            )

        if upper <= 0:
            raise InvalidDistributionParameterException(
                line_number,
                f'loguniform distribution parameter `upper={upper}` not positive',
            )

        self.lower = lower
        self.upper = upper
        super().__init__(line_number)

    def generate_samples(self, count: int) -> list[float]:
        a = self.lower
        b = self.upper

        return [math.exp(random.uniform(math.log(a), math.log(b))) for _ in range(count)]


class NormalDistribution(Distribution):
    def __init__(self, mu: float, sigma: float, line_number: int):
        self.mu = mu
        self.sigma = sigma
        super().__init__(line_number)

    def generate_samples(self, count: int) -> list[float]:
        mu = self.mu
        sigma = self.sigma

        return [random.normalvariate(mu, sigma) for _ in range(count)]


class TriangularDistribution(Distribution):
    def __init__(self, lower: float, upper: float, mode: float, line_number: int):
        self.lower = lower
        self.upper = upper
        self.mode = mode
        super().__init__(line_number)

    def generate_samples(self, count: int) -> list[float]:
        low = self.lower
        high = self.upper
        mode = self.mode

        return [random.triangular(low, high, mode) for _ in range(count)]


class UniformDistribution(Distribution):
    def __init__(self, lower: float, upper: float, line_number: int):
        self.lower = lower
        self.upper = upper
        super().__init__(line_number)

    def generate_samples(self, count: int) -> list[float]:
        a = self.lower
        b = self.upper

        return [random.uniform(a, b) for _ in range(count)]
