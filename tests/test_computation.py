"""
# Public Fault Tree Analyser: test_computation.py

Unit testing for `computation.py`.

**Copyright 2025 Conway.**
Licensed under the GNU General Public License v3.0 (GPL-3.0-only).
This is free software with NO WARRANTY etc. etc., see LICENSE.
"""

import math
import unittest

from pfta.computation import constant_rate_model_probability, constant_rate_model_intensity

INF = float('inf')
NAN = float('nan')


class TestComputation(unittest.TestCase):

    def test_constant_rate_model_probability(self):
        self.assertTrue(math.isnan(constant_rate_model_probability(lambda_=0, mu=0, t=INF)))
        self.assertTrue(math.isnan(constant_rate_model_probability(lambda_=0, mu=0, t=NAN)))

        self.assertEqual(constant_rate_model_probability(lambda_=0, mu=0, t=0), 0.)
        self.assertEqual(constant_rate_model_probability(lambda_=0, mu=0, t=1), 0.)

        self.assertEqual(constant_rate_model_probability(lambda_=0, mu=INF, t=INF), 0.)
        self.assertEqual(constant_rate_model_probability(lambda_=0, mu=INF, t=NAN), 0.)
        self.assertEqual(constant_rate_model_probability(lambda_=0, mu=INF, t=0), 0.)
        self.assertEqual(constant_rate_model_probability(lambda_=0, mu=INF, t=1), 0.)

        self.assertTrue(math.isnan(constant_rate_model_probability(lambda_=0, mu=NAN, t=INF)))
        self.assertTrue(math.isnan(constant_rate_model_probability(lambda_=0, mu=NAN, t=NAN)))

        self.assertEqual(constant_rate_model_probability(lambda_=0, mu=NAN, t=0), 0.)
        self.assertEqual(constant_rate_model_probability(lambda_=0, mu=NAN, t=1), 0.)

        self.assertEqual(constant_rate_model_probability(lambda_=0, mu=1, t=INF), 0.)
        self.assertEqual(constant_rate_model_probability(lambda_=0, mu=1, t=NAN), 0.)
        self.assertEqual(constant_rate_model_probability(lambda_=0, mu=1, t=0), 0.)
        self.assertEqual(constant_rate_model_probability(lambda_=0, mu=1, t=1), 0.)

        self.assertTrue(math.isnan(constant_rate_model_probability(lambda_=INF, mu=INF, t=INF)))
        self.assertTrue(math.isnan(constant_rate_model_probability(lambda_=INF, mu=INF, t=NAN)))
        self.assertTrue(math.isnan(constant_rate_model_probability(lambda_=INF, mu=INF, t=0)))
        self.assertTrue(math.isnan(constant_rate_model_probability(lambda_=INF, mu=INF, t=1)))
        self.assertTrue(math.isnan(constant_rate_model_probability(lambda_=INF, mu=NAN, t=INF)))
        self.assertTrue(math.isnan(constant_rate_model_probability(lambda_=INF, mu=NAN, t=NAN)))
        self.assertTrue(math.isnan(constant_rate_model_probability(lambda_=INF, mu=NAN, t=0)))
        self.assertTrue(math.isnan(constant_rate_model_probability(lambda_=INF, mu=NAN, t=1)))

        self.assertTrue(math.isnan(constant_rate_model_probability(lambda_=INF, mu=0, t=NAN)))
        self.assertTrue(math.isnan(constant_rate_model_probability(lambda_=INF, mu=0, t=0)))
        self.assertTrue(math.isnan(constant_rate_model_probability(lambda_=INF, mu=1, t=NAN)))
        self.assertTrue(math.isnan(constant_rate_model_probability(lambda_=INF, mu=1, t=0)))

        self.assertEqual(constant_rate_model_probability(lambda_=INF, mu=0, t=INF), 1.)
        self.assertEqual(constant_rate_model_probability(lambda_=INF, mu=0, t=1), 1.)
        self.assertEqual(constant_rate_model_probability(lambda_=INF, mu=1, t=INF), 1.)
        self.assertEqual(constant_rate_model_probability(lambda_=INF, mu=1, t=1), 1.)

        self.assertTrue(math.isnan(constant_rate_model_probability(lambda_=NAN, mu=0, t=INF)))
        self.assertTrue(math.isnan(constant_rate_model_probability(lambda_=NAN, mu=0, t=NAN)))

        self.assertTrue(math.isnan(constant_rate_model_probability(lambda_=NAN, mu=0, t=0)))
        self.assertTrue(math.isnan(constant_rate_model_probability(lambda_=NAN, mu=0, t=1)))

        self.assertTrue(math.isnan(constant_rate_model_probability(lambda_=NAN, mu=INF, t=INF)))
        self.assertTrue(math.isnan(constant_rate_model_probability(lambda_=NAN, mu=INF, t=NAN)))
        self.assertTrue(math.isnan(constant_rate_model_probability(lambda_=NAN, mu=INF, t=0)))
        self.assertTrue(math.isnan(constant_rate_model_probability(lambda_=NAN, mu=INF, t=1)))
        self.assertTrue(math.isnan(constant_rate_model_probability(lambda_=NAN, mu=NAN, t=INF)))
        self.assertTrue(math.isnan(constant_rate_model_probability(lambda_=NAN, mu=NAN, t=NAN)))
        self.assertTrue(math.isnan(constant_rate_model_probability(lambda_=NAN, mu=NAN, t=0)))
        self.assertTrue(math.isnan(constant_rate_model_probability(lambda_=NAN, mu=NAN, t=1)))

        self.assertTrue(math.isnan(constant_rate_model_probability(lambda_=NAN, mu=1, t=INF)))
        self.assertTrue(math.isnan(constant_rate_model_probability(lambda_=NAN, mu=1, t=NAN)))
        self.assertTrue(math.isnan(constant_rate_model_probability(lambda_=NAN, mu=1, t=0)))
        self.assertTrue(math.isnan(constant_rate_model_probability(lambda_=NAN, mu=1, t=1)))

        self.assertEqual(constant_rate_model_probability(lambda_=1, mu=INF, t=INF), 0.)
        self.assertEqual(constant_rate_model_probability(lambda_=1, mu=INF, t=NAN), 0.)
        self.assertEqual(constant_rate_model_probability(lambda_=1, mu=INF, t=0), 0.)
        self.assertEqual(constant_rate_model_probability(lambda_=1, mu=INF, t=1), 0.)

        self.assertTrue(math.isnan(constant_rate_model_probability(lambda_=1, mu=NAN, t=INF)))

        self.assertTrue(math.isnan(constant_rate_model_probability(lambda_=1, mu=NAN, t=NAN)))
        self.assertTrue(math.isnan(constant_rate_model_probability(lambda_=1, mu=NAN, t=0)))
        self.assertTrue(math.isnan(constant_rate_model_probability(lambda_=1, mu=NAN, t=1)))

        self.assertTrue(
            math.isclose(
                constant_rate_model_probability(lambda_=1, mu=0, t=math.log(2)),
                1/2,
                rel_tol=1e-15,
            ),
        )
        self.assertTrue(
            math.isclose(
                constant_rate_model_probability(lambda_=69, mu=420, t=INF),
                69/(69+420),
                rel_tol=1e-15,
            ),
        )
        self.assertTrue(
            math.isclose(
                constant_rate_model_probability(lambda_=3, mu=4, t=5),
                0.4285714285714283012092817079861691868990917608624530832108001585160503999788026,  # WolframAlpha
                rel_tol=1e-15,
            ),
        )
        self.assertTrue(
            math.isclose(
                constant_rate_model_probability(lambda_=1e-13, mu=1e-14, t=1),
                9.99999999999945000000000002016666666666611208333333334553416666666644298472222e-14,  # WolframAlpha
                rel_tol=1e-15,
            ),
        )

    def test_constant_rate_model_intensity(self):
        self.assertEqual(constant_rate_model_intensity(lambda_=0, mu=INF, t=INF), 0.)
        self.assertEqual(constant_rate_model_intensity(lambda_=0, mu=INF, t=NAN), 0.)
        self.assertEqual(constant_rate_model_intensity(lambda_=0, mu=INF, t=0), 0.)
        self.assertEqual(constant_rate_model_intensity(lambda_=0, mu=INF, t=1), 0.)
        self.assertEqual(constant_rate_model_intensity(lambda_=0, mu=NAN, t=INF), 0.)
        self.assertEqual(constant_rate_model_intensity(lambda_=0, mu=NAN, t=NAN), 0.)
        self.assertEqual(constant_rate_model_intensity(lambda_=0, mu=NAN, t=0), 0.)
        self.assertEqual(constant_rate_model_intensity(lambda_=0, mu=NAN, t=1), 0.)
        self.assertEqual(constant_rate_model_intensity(lambda_=0, mu=0, t=INF), 0.)
        self.assertEqual(constant_rate_model_intensity(lambda_=0, mu=0, t=NAN), 0.)
        self.assertEqual(constant_rate_model_intensity(lambda_=0, mu=0, t=0), 0.)
        self.assertEqual(constant_rate_model_intensity(lambda_=0, mu=0, t=1), 0.)
        self.assertEqual(constant_rate_model_intensity(lambda_=0, mu=1, t=INF), 0.)
        self.assertEqual(constant_rate_model_intensity(lambda_=0, mu=1, t=NAN), 0.)
        self.assertEqual(constant_rate_model_intensity(lambda_=0, mu=1, t=0), 0.)
        self.assertEqual(constant_rate_model_intensity(lambda_=0, mu=1, t=1), 0.)

        self.assertTrue(math.isnan(constant_rate_model_intensity(lambda_=INF, mu=INF, t=INF)))
        self.assertTrue(math.isnan(constant_rate_model_intensity(lambda_=INF, mu=INF, t=NAN)))
        self.assertTrue(math.isnan(constant_rate_model_intensity(lambda_=INF, mu=INF, t=0)))
        self.assertTrue(math.isnan(constant_rate_model_intensity(lambda_=INF, mu=INF, t=1)))
        self.assertTrue(math.isnan(constant_rate_model_intensity(lambda_=INF, mu=NAN, t=INF)))
        self.assertTrue(math.isnan(constant_rate_model_intensity(lambda_=INF, mu=NAN, t=NAN)))
        self.assertTrue(math.isnan(constant_rate_model_intensity(lambda_=INF, mu=NAN, t=0)))
        self.assertTrue(math.isnan(constant_rate_model_intensity(lambda_=INF, mu=NAN, t=1)))

        self.assertTrue(math.isnan(constant_rate_model_intensity(lambda_=INF, mu=0, t=0)))
        self.assertTrue(math.isnan(constant_rate_model_intensity(lambda_=INF, mu=0, t=NAN)))
        self.assertTrue(math.isnan(constant_rate_model_intensity(lambda_=INF, mu=1, t=0)))
        self.assertTrue(math.isnan(constant_rate_model_intensity(lambda_=INF, mu=1, t=NAN)))

        self.assertEqual(constant_rate_model_intensity(lambda_=INF, mu=0, t=INF), 0)
        self.assertEqual(constant_rate_model_intensity(lambda_=INF, mu=0, t=1), 0)
        self.assertEqual(constant_rate_model_intensity(lambda_=INF, mu=1, t=INF), 1)
        self.assertEqual(constant_rate_model_intensity(lambda_=INF, mu=1, t=1), 1)
        self.assertEqual(constant_rate_model_intensity(lambda_=INF, mu=2.3, t=1), 2.3)
        self.assertEqual(constant_rate_model_intensity(lambda_=INF, mu=1e100, t=34567), 1e100)

        self.assertTrue(math.isnan(constant_rate_model_intensity(lambda_=NAN, mu=INF, t=INF)))
        self.assertTrue(math.isnan(constant_rate_model_intensity(lambda_=NAN, mu=INF, t=NAN)))
        self.assertTrue(math.isnan(constant_rate_model_intensity(lambda_=NAN, mu=INF, t=0)))
        self.assertTrue(math.isnan(constant_rate_model_intensity(lambda_=NAN, mu=INF, t=1)))
        self.assertTrue(math.isnan(constant_rate_model_intensity(lambda_=NAN, mu=NAN, t=INF)))
        self.assertTrue(math.isnan(constant_rate_model_intensity(lambda_=NAN, mu=NAN, t=NAN)))
        self.assertTrue(math.isnan(constant_rate_model_intensity(lambda_=NAN, mu=NAN, t=0)))
        self.assertTrue(math.isnan(constant_rate_model_intensity(lambda_=NAN, mu=NAN, t=1)))

        self.assertTrue(math.isnan(constant_rate_model_intensity(lambda_=NAN, mu=0, t=0)))
        self.assertTrue(math.isnan(constant_rate_model_intensity(lambda_=NAN, mu=0, t=NAN)))
        self.assertTrue(math.isnan(constant_rate_model_intensity(lambda_=NAN, mu=1, t=0)))
        self.assertTrue(math.isnan(constant_rate_model_intensity(lambda_=NAN, mu=1, t=NAN)))

        self.assertTrue(math.isnan(constant_rate_model_intensity(lambda_=NAN, mu=0, t=INF)))
        self.assertTrue(math.isnan(constant_rate_model_intensity(lambda_=NAN, mu=0, t=1)))
        self.assertTrue(math.isnan(constant_rate_model_intensity(lambda_=NAN, mu=1, t=INF)))
        self.assertTrue(math.isnan(constant_rate_model_intensity(lambda_=NAN, mu=1, t=1)))

        self.assertEqual(constant_rate_model_intensity(lambda_=1, mu=INF, t=INF), 1)
        self.assertEqual(constant_rate_model_intensity(lambda_=1, mu=INF, t=NAN), 1)
        self.assertEqual(constant_rate_model_intensity(lambda_=1, mu=INF, t=0), 1)
        self.assertEqual(constant_rate_model_intensity(lambda_=1, mu=INF, t=1), 1)
        self.assertEqual(constant_rate_model_intensity(lambda_=2.3, mu=INF, t=34567), 2.3)
        self.assertEqual(constant_rate_model_intensity(lambda_=1e100, mu=INF, t=34567), 1e100)

        self.assertTrue(math.isnan(constant_rate_model_intensity(lambda_=1, mu=NAN, t=INF)))
        self.assertTrue(math.isnan(constant_rate_model_intensity(lambda_=1, mu=NAN, t=NAN)))
        self.assertTrue(math.isnan(constant_rate_model_intensity(lambda_=1, mu=NAN, t=0)))
        self.assertTrue(math.isnan(constant_rate_model_intensity(lambda_=1, mu=NAN, t=1)))

        self.assertTrue(
            math.isclose(
                constant_rate_model_intensity(lambda_=1, mu=0, t=math.log(2)),
                1/2,
                rel_tol=1e-15,
            ),
        )
        self.assertTrue(
            math.isclose(
                constant_rate_model_intensity(lambda_=69, mu=420, t=INF),
                69 * 420/(69+420),
                rel_tol=1e-15,
            ),
        )
        self.assertTrue(
            math.isclose(
                constant_rate_model_intensity(lambda_=3, mu=4, t=5),
                1.714285714285715096372154876041492439302724717412640750367599524451848800063592,  # WolframAlpha
                rel_tol=1e-15,
            ),
        )
        self.assertTrue(
            math.isclose(
                constant_rate_model_intensity(lambda_=1e-13, mu=1e-14, t=1),
                9.99999999999900000000000005499999999999798333333333338879166666666544658333333e-14,  # WolframAlpha
                rel_tol=1e-15,
            ),
        )
