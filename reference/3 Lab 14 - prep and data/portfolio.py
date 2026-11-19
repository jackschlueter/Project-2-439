"""Calculate the three Meridian training portfolios from the course inputs."""

from math import isclose, isfinite, sqrt


SLEEVES = ("Bills", "10-year", "IG bonds", "Equity")
RETURNS = (0.035, 0.043, 0.050, 0.080)
VOLATILITIES = (0.005, 0.070, 0.060, 0.160)
CORRELATIONS = (
    (1.00, 0.10, 0.05, 0.00),
    (0.10, 1.00, 0.80, -0.10),
    (0.05, 0.80, 1.00, 0.25),
    (0.00, -0.10, 0.25, 1.00),
)
RETURN_TARGET = 0.065  # 2.5% estimated CPI + 4.0%.
RESERVE_MINIMUM = 0.03


def validate_inputs(weights, correlations):
    count = len(SLEEVES)
    if len(weights) != count or any(not isfinite(w) or w < 0 for w in weights):
        raise ValueError("Weights must be finite, nonnegative, and match the sleeves")
    if not isclose(sum(weights), 1.0, rel_tol=0, abs_tol=1e-9):
        raise ValueError("Weights must sum to 1")
    if len(correlations) != count or any(len(row) != count for row in correlations):
        raise ValueError("Correlation matrix must be 4 by 4")
    for i in range(count):
        if not isclose(correlations[i][i], 1.0, rel_tol=0, abs_tol=1e-9):
            raise ValueError("Diagonal correlations must equal 1")
        for j in range(count):
            value = correlations[i][j]
            if not isfinite(value) or not -1.0 <= value <= 1.0:
                raise ValueError("Correlations must be between -1 and 1")
            if not isclose(value, correlations[j][i], rel_tol=0, abs_tol=1e-9):
                raise ValueError("Correlation matrix must be symmetric")


def portfolio_stats(weights, correlations=CORRELATIONS):
    validate_inputs(weights, correlations)
    expected_return = sum(w * r for w, r in zip(weights, RETURNS))
    variance = sum(
        weights[i] * weights[j] * VOLATILITIES[i] * VOLATILITIES[j]
        * correlations[i][j]
        for i in range(len(SLEEVES))
        for j in range(len(SLEEVES))
    )
    if variance < 0:
        raise ValueError("Correlation matrix produced negative portfolio variance")
    volatility = sqrt(variance)
    reserve_eligible = weights[0] + weights[1]
    return expected_return, volatility, reserve_eligible


def main():
    inverse = [1 / volatility for volatility in VOLATILITIES]
    inverse_total = sum(inverse)
    portfolios = {
        "Benchmark": (0.0, 0.0, 0.4, 0.6),
        "Equal weight": (0.25, 0.25, 0.25, 0.25),
        "Inverse volatility": tuple(value / inverse_total for value in inverse),
    }

    print("Portfolio | Weights: bills / 10-year / IG / equity | Return | Volatility | Reserve eligible | Meets 6.5%?")
    for name, weights in portfolios.items():
        expected_return, volatility, reserve = portfolio_stats(weights)
        shown_weights = " / ".join(f"{100 * weight:.1f}" for weight in weights)
        print(
            f"{name} | {shown_weights} | {100 * expected_return:.2f}% | "
            f"{100 * volatility:.2f}% | {100 * reserve:.1f}% | "
            f"{'yes' if expected_return >= RETURN_TARGET else 'no'}"
        )
        print(f"  Reserve floor: {'pass' if reserve >= RESERVE_MINIMUM else 'FAIL'}")


if __name__ == "__main__":
    main()
