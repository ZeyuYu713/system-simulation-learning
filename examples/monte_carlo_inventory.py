"""Monte Carlo inventory comparison with a known exact answer.

Demand:       0, 1, 2, 3 with probabilities 0.1, 0.2, 0.4, 0.3.
Holding cost: 2 per leftover unit.
Shortage cost:4 per missing unit.
Compare stocks 1, 2, 3 using the SAME simulated demands.

Run: python examples/monte_carlo_inventory.py
Requires Python 3.10+ and only the standard library.
"""

from __future__ import annotations

from math import sqrt
from random import Random


DEMAND = (0, 1, 2, 3)
PROBABILITY = (0.1, 0.2, 0.4, 0.3)
STOCK_LEVELS = (1, 2, 3)
HOLDING_COST = 2
SHORTAGE_COST = 4


def sample_demand(u: float) -> int:
    """Inverse-CDF sampling for a discrete demand distribution."""
    if not 0 <= u < 1:
        raise ValueError("u must be in [0, 1)")
    cumulative = 0.0
    for demand, probability in zip(DEMAND, PROBABILITY):
        cumulative += probability
        if u < cumulative:
            return demand
    return DEMAND[-1]  # Protect against floating-point rounding.


def cost(stock: int, demand: int) -> float:
    return HOLDING_COST * max(stock - demand, 0) + SHORTAGE_COST * max(
        demand - stock, 0
    )


def exact_expected_cost(stock: int) -> float:
    return sum(
        probability * cost(stock, demand)
        for demand, probability in zip(DEMAND, PROBABILITY)
    )


def monte_carlo(n: int = 100_000, seed: int = 2026) -> dict[int, tuple[float, float]]:
    """Return (sample mean, standard error) for each stock policy."""
    if n < 2:
        raise ValueError("n must be at least 2 to estimate standard error")
    rng = Random(seed)
    total = {stock: 0.0 for stock in STOCK_LEVELS}
    total_squared = {stock: 0.0 for stock in STOCK_LEVELS}

    for _ in range(n):
        demand = sample_demand(rng.random())
        # All policies face the same demand on each Monte Carlo iteration.
        for stock in STOCK_LEVELS:
            value = cost(stock, demand)
            total[stock] += value
            total_squared[stock] += value * value

    result = {}
    for stock in STOCK_LEVELS:
        mean = total[stock] / n
        sample_variance = (total_squared[stock] - n * mean * mean) / (n - 1)
        standard_error = sqrt(max(sample_variance, 0.0) / n)
        result[stock] = (mean, standard_error)
    return result


def main() -> None:
    n, seed = 100_000, 2026
    estimates = monte_carlo(n=n, seed=seed)
    print(f"Simulations: {n:,}  |  seed: {seed}")
    print("Stock  Exact E[cost]  MC mean     MC SE      Approx. 95% CI")
    for stock in STOCK_LEVELS:
        exact = exact_expected_cost(stock)
        mean, se = estimates[stock]
        lower, upper = mean - 1.96 * se, mean + 1.96 * se
        print(
            f"{stock:>5}  {exact:>13.4f}  {mean:>9.4f}  "
            f"{se:>8.4f}  [{lower:.4f}, {upper:.4f}]"
        )

    exact_values = [exact_expected_cost(stock) for stock in STOCK_LEVELS]
    assert all(abs(a - b) < 1e-12 for a, b in zip(exact_values, (4.2, 2.0, 2.2)))
    assert all(
        abs(estimates[stock][0] - exact_expected_cost(stock)) < 0.06
        for stock in STOCK_LEVELS
    )
    print("Self-check passed: Monte Carlo estimates approach exact expectations.")


if __name__ == "__main__":
    main()
