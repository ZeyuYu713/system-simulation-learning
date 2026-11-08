"""Reproduce deterministic input-modeling examples (Python 3.10+, stdlib only)."""

from __future__ import annotations

import math
import random
from statistics import mean


def intervals_from_arrivals(arrivals: list[float]) -> list[float]:
    if len(arrivals) < 2 or any(
        right <= left for left, right in zip(arrivals, arrivals[1:])
    ):
        raise ValueError("Arrival timestamps must be strictly increasing.")
    return [right - left for left, right in zip(arrivals, arrivals[1:])]


def exponential_rate_mle(samples: list[float]) -> float:
    if not samples or any(value <= 0 for value in samples):
        raise ValueError("Exponential samples must be positive.")
    return len(samples) / sum(samples)


def ks_one_sample_continuous(
    samples: list[float], cdf
) -> tuple[float, float, float]:
    """Return D+, D-, D for the fully specified continuous reference CDF.

    This routine calculates the statistic, NOT a calibrated p-value. It must
    not be paired with ordinary KS critical values after fitting parameters
    on the same observations.
    """
    xs = sorted(samples)
    n = len(xs)
    if n == 0:
        raise ValueError("The sample must not be empty.")
    d_plus = max((index + 1) / n - cdf(x) for index, x in enumerate(xs))
    d_minus = max(cdf(x) - index / n for index, x in enumerate(xs))
    return d_plus, d_minus, max(d_plus, d_minus)


def chi_square_stat(observed: list[int], expected: list[float]) -> float:
    if len(observed) != len(expected) or any(value <= 0 for value in expected):
        raise ValueError("Expected frequencies must be positive and aligned.")
    if not math.isclose(sum(observed), sum(expected)):
        raise ValueError("Expected and observed totals must be equal.")
    return sum((o - e) ** 2 / e for o, e in zip(observed, expected))


def triangular_inverse(u: float, low: float, mode: float, high: float) -> float:
    if not (0 <= u <= 1 and low < mode < high):
        raise ValueError("Require 0<=u<=1 and low<mode<high.")
    threshold = (mode - low) / (high - low)
    if u < threshold:
        return low + math.sqrt(u * (high - low) * (mode - low))
    return high - math.sqrt((1 - u) * (high - low) * (high - mode))


def empirical_discrete(u: float, values: list[int], probabilities: list[float]) -> int:
    if (
        not 0 <= u < 1
        or len(values) != len(probabilities)
        or any(p < 0 for p in probabilities)
        or not math.isclose(sum(probabilities), 1)
    ):
        raise ValueError("Probabilities must sum to one.")
    cumulative = 0.0
    for value, probability in zip(values, probabilities):
        cumulative += probability
        if u < cumulative:
            return value
    return values[-1]


def bootstrap_rates(samples: list[float], repetitions: int = 2000) -> tuple[float, float]:
    rng = random.Random(2026)
    estimates = []
    for _ in range(repetitions):
        resampled = [rng.choice(samples) for _ in samples]
        estimates.append(exponential_rate_mle(resampled))
    estimates.sort()
    return estimates[int(0.025 * repetitions)], estimates[int(0.975 * repetitions)]


def main() -> None:
    arrivals = [0, 2, 3, 6, 10]
    intervals = intervals_from_arrivals(arrivals)
    rate = exponential_rate_mle(intervals)
    generated_interval = -math.log(1 - 0.8) / rate
    assert intervals == [2, 1, 3, 4]
    assert math.isclose(rate, 0.4)
    assert math.isclose(generated_interval, 4.023594781085251)
    print(f"Arrivals: intervals={intervals}, rate={rate:.3f}/min, inverse={generated_interval:.3f} min")

    d_plus, d_minus, d = ks_one_sample_continuous(
        [0.1, 0.3, 0.7, 0.9], lambda x: x
    )
    assert all(math.isclose(x, 0.2) for x in (d_plus, d_minus, d))
    print(f"Fully specified U(0,1) KS: D+={d_plus:.3f}, D-={d_minus:.3f}, D={d:.3f}")

    chi2 = chi_square_stat([21, 29, 26, 24], [25.0] * 4)
    assert math.isclose(chi2, 1.36)
    print(f"Four-class chi-square statistic: {chi2:.3f}, df=3 (all probabilities fixed)")

    triangle = triangular_inverse(0.75, 1, 2, 5)
    assert math.isclose(triangle, 5 - math.sqrt(3))
    demand = empirical_discrete(0.65, [0, 1, 2, 3], [0.1, 0.2, 0.4, 0.3])
    assert demand == 2
    print(f"Triangular inverse={triangle:.3f} h, empirical discrete demand={demand}")

    segmented_expected = [2 * rate for rate in (3, 8, 4)]
    assert segmented_expected == [6, 16, 8]
    assert math.isclose(mean(segmented_expected), 10)
    print(f"Piecewise Poisson interval expectations={segmented_expected}, flat approximation=[10,10,10]")

    logdata = [0.0, 1.0, 2.0]
    log_mu = mean(logdata)
    log_var_mle = mean([(value - log_mu) ** 2 for value in logdata])
    lognormal_mean = math.exp(log_mu + log_var_mle / 2)
    assert math.isclose(log_mu, 1)
    assert math.isclose(log_var_mle, 2 / 3)
    print(f"Lognormal example: mu={log_mu:.3f}, sigma^2={log_var_mle:.3f}, E[X]={lognormal_mean:.3f}")

    bootstrap_low, bootstrap_high = bootstrap_rates(intervals)
    assert bootstrap_low <= rate <= bootstrap_high
    print(f"Illustrative percentile bootstrap range for rate: [{bootstrap_low:.3f}, {bootstrap_high:.3f}]")
    print("All input-modeling checks passed.")


if __name__ == "__main__":
    main()
