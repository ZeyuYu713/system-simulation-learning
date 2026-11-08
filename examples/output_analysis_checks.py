"""Reproduce the numerical examples in the output-analysis chapter.

Run with Python 3.10+; no third-party packages are required.
"""

from __future__ import annotations

from fractions import Fraction
from math import isclose, sqrt
from statistics import mean, variance


# Student t, 97.5% quantile for four degrees of freedom.
# This constant is appropriate for the 5-observation examples below only.
T_975_DF4 = 2.7764451051977987


def mean_ci_five(values: list[float]) -> tuple[float, float, float]:
    """Return mean, standard error, and 95% CI half-width for five values."""
    assert len(values) == 5
    center = mean(values)
    standard_error = sqrt(variance(values) / len(values))
    return center, standard_error, T_975_DF4 * standard_error


def queue_area() -> tuple[float, float, float]:
    """Three customers: arrive 0/1/2, start 0/3/5, finish 3/5/6."""
    arrivals = [0, 1, 2]
    starts = [0, 3, 5]
    finishes = [3, 5, 6]
    waiting = [begin - arrival for arrival, begin in zip(arrivals, starts)]

    # Intervals [0,1), [1,2), [2,3), [3,5), [5,6)
    queue_levels = [0, 1, 2, 1, 0]
    boundaries = [0, 1, 2, 3, 5, 6]
    area = sum(
        level * (right - left)
        for level, left, right in zip(queue_levels, boundaries, boundaries[1:])
    )
    horizon = finishes[-1]
    return mean(waiting), area / horizon, len(arrivals) / horizon


def paired_comparison() -> tuple[float, float, float]:
    a = [12, 10, 14, 11, 13]
    b = [10, 9, 11, 10, 10]
    differences = [x - y for x, y in zip(a, b)]
    center, paired_se, half_width = mean_ci_five(differences)
    independent_se = sqrt(variance(a) / len(a) + variance(b) / len(b))
    assert isclose(center, 2)
    assert isclose(variance(differences), 1)
    assert paired_se < independent_se
    return paired_se, independent_se, half_width


def exact_variance_reduction() -> tuple[Fraction, Fraction, Fraction]:
    """Y=U^2, antithetic Y'=(1-U)^2, control C=U."""
    var_y = Fraction(1, 5) - Fraction(1, 3) ** 2
    cov_antithetic = Fraction(1, 30) - Fraction(1, 3) ** 2
    antithetic_pair_variance = (2 * var_y + 2 * cov_antithetic) / 4
    cov_control = Fraction(1, 4) - Fraction(1, 3) * Fraction(1, 2)
    var_control = Fraction(1, 12)
    beta = cov_control / var_control
    adjusted_variance = var_y - cov_control**2 / var_control
    return antithetic_pair_variance, beta, adjusted_variance


def main() -> None:
    avg_wait, avg_queue, effective_arrival_rate = queue_area()
    assert isclose(avg_wait, 5 / 3)
    assert isclose(avg_queue, 5 / 6)
    assert isclose(avg_queue, effective_arrival_rate * avg_wait)
    print(f"Queue: mean Wq={avg_wait:.6f}, time-average Lq={avg_queue:.6f}")

    center, se, half_width = mean_ci_five([4, 5, 6, 7, 8])
    assert isclose(center, 6)
    assert isclose(variance([4, 5, 6, 7, 8]), 2.5)
    print(f"Five replications: mean={center:.3f}, SE={se:.3f}, "
          f"95% CI=[{center-half_width:.3f}, {center+half_width:.3f}]")

    paired_se, independent_se, paired_half = paired_comparison()
    assert isclose(paired_se, sqrt(1 / 5))
    assert isclose(independent_se, sqrt(3 / 5))
    print(f"Two systems: paired SE={paired_se:.3f}, "
          f"independent SE={independent_se:.3f}, "
          f"paired 95% CI=[{2-paired_half:.3f}, {2+paired_half:.3f}]")

    pair_var, beta, control_var = exact_variance_reduction()
    assert pair_var == Fraction(1, 180)
    assert beta == 1
    assert control_var == Fraction(1, 180)
    print(f"Variance reduction: antithetic pair var={pair_var}, "
          f"control beta={beta}, control var={control_var}")

    base_mean = (0 * 10 + 4 * 90) / 100
    assert isclose(base_mean, 3.6)
    print(f"Warm-up illustration: untrimmed mean={base_mean:.1f}, trimmed mean=4.0")

    print("All output-analysis examples passed.")


if __name__ == "__main__":
    main()
