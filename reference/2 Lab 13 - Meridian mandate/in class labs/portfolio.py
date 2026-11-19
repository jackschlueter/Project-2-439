"""Meridian baselines and a minimum-risk engine for course or price estimates."""

import csv
from datetime import datetime
from io import StringIO
from itertools import combinations
from math import isclose, isfinite, sqrt
from pathlib import Path

import numpy as np


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
RESERVE_ELIGIBLE = (1.0, 1.0, 0.0, 0.0)


def validate_inputs(weights, correlations):
    count = len(weights)
    if count == 0:
        raise ValueError("At least one asset is required")
    if any(not isfinite(w) or w < 0 for w in weights):
        raise ValueError("Weights must be finite and nonnegative")
    if not isclose(sum(weights), 1.0, rel_tol=0, abs_tol=1e-9):
        raise ValueError("Weights must sum to 1")
    if len(correlations) != count or any(len(row) != count for row in correlations):
        raise ValueError("Correlation matrix must match the assets")
    for i in range(count):
        if not isclose(correlations[i][i], 1.0, rel_tol=0, abs_tol=1e-9):
            raise ValueError("Diagonal correlations must equal 1")
        for j in range(count):
            value = correlations[i][j]
            if not isfinite(value) or not -1.0 <= value <= 1.0:
                raise ValueError("Correlations must be between -1 and 1")
            if not isclose(value, correlations[j][i], rel_tol=0, abs_tol=1e-9):
                raise ValueError("Correlation matrix must be symmetric")


def portfolio_stats(weights, correlations=CORRELATIONS, returns=RETURNS,
                    volatilities=VOLATILITIES,
                    reserve_eligible=RESERVE_ELIGIBLE):
    validate_inputs(weights, correlations)
    count = len(weights)
    if (len(returns) != count or len(volatilities) != count
            or len(reserve_eligible) != count
            or any(not isfinite(x) for x in returns)
            or any(not isfinite(x) or x < 0 for x in volatilities)
            or any(x not in (0, 1) for x in reserve_eligible)):
        raise ValueError("Returns, volatilities, and reserve eligibility must match the assets")
    expected_return = sum(w * r for w, r in zip(weights, returns))
    variance = sum(
        weights[i] * weights[j] * volatilities[i] * volatilities[j]
        * correlations[i][j]
        for i in range(count)
        for j in range(count)
    )
    if variance < 0:
        raise ValueError("Correlation matrix produced negative portfolio variance")
    volatility = sqrt(variance)
    reserve_share = sum(w * eligible for w, eligible in zip(weights, reserve_eligible))
    return expected_return, volatility, reserve_share


def optimize_portfolio(target=RETURN_TARGET, reserve_minimum=RESERVE_MINIMUM,
                       returns=RETURNS, volatilities=VOLATILITIES,
                       correlations=CORRELATIONS,
                       reserve_eligible=RESERVE_ELIGIBLE):
    """Find the long-only minimum-variance mix meeting return and reserve floors."""
    if (not isfinite(target) or not isfinite(reserve_minimum)
            or not 0 <= reserve_minimum <= 1):
        raise ValueError("Target and reserve minimum must be finite; reserve is 0–100%")
    count = len(returns)
    if count == 0:
        raise ValueError("At least one asset is required")
    portfolio_stats((1.0,) + (0.0,) * (count - 1), correlations, returns,
                    volatilities, reserve_eligible)
    covariance = np.outer(volatilities, volatilities) * np.asarray(correlations)
    if np.linalg.eigvalsh(covariance).min() < -1e-12:
        raise ValueError("Correlation inputs produce an invalid covariance matrix")

    reserve = np.asarray(reserve_eligible)
    possible_constraints = [
        (np.eye(count)[i], 0.0) for i in range(count)
    ] + [(np.asarray(returns), target), (reserve, reserve_minimum)]
    best = None
    for active_count in range(count + 1):
        for active in combinations(possible_constraints, active_count):
            rows = [np.ones(count)] + [item[0] for item in active]
            bounds = [1.0] + [item[1] for item in active]
            a = np.asarray(rows)
            kkt = np.block([[2 * covariance, a.T],
                            [a, np.zeros((len(rows), len(rows)))]])
            solution, *_ = np.linalg.lstsq(
                kkt, np.r_[np.zeros(count), bounds], rcond=None
            )
            if np.max(np.abs(kkt @ solution - np.r_[np.zeros(count), bounds])) > 1e-8:
                continue
            weights = solution[:count]
            if (weights.min() < -1e-8
                    or np.dot(weights, returns) < target - 1e-8
                    or np.dot(weights, reserve) < reserve_minimum - 1e-8):
                continue
            variance = float(weights @ covariance @ weights)
            if best is None or variance < best[0]:
                best = (variance, weights)
    if best is None:
        raise ValueError("No long-only mix can meet both the return target and reserve floor")
    weights = tuple(float(max(0.0, value)) for value in best[1])
    expected_return, volatility, reserve_share = portfolio_stats(
        weights, correlations, returns, volatilities, reserve_eligible
    )
    return weights, expected_return, volatility, reserve_share


def load_historical_estimates(path=Path(__file__).with_name("prices.csv")):
    """Keep the existing all-month estimate interface for the saved price panel."""
    result = estimate_from_csv(path)
    if result[4][2] != 60:
        raise ValueError("Expected 60 monthly returns in the saved price panel")
    return result


def estimate_from_csv(source, last_36=False):
    """Estimate annualized means, volatilities, and correlations from prices."""
    if isinstance(source, (str, Path)):
        raw = Path(source).read_text()
    elif hasattr(source, "getvalue"):
        raw = source.getvalue()
    else:
        raw = source.read()
    if isinstance(raw, bytes):
        raw = raw.decode("utf-8-sig")
    reader = csv.reader(StringIO(raw))
    header = next(reader, None)
    if not header or not header[0] or not 3 <= len(header) - 1 <= 6:
        raise ValueError("CSV needs a date column followed by three to six tickers")
    tickers = tuple(header[1:])
    if any(not ticker for ticker in tickers) or len(set(tickers)) != len(tickers):
        raise ValueError("Ticker columns must be named and unique")
    rows = list(reader)
    if any(len(row) != len(header) for row in rows):
        raise ValueError("Every CSV row must have a date and all ticker prices")
    try:
        dates = [datetime.strptime(row[0], "%Y-%m") for row in rows]
        prices = np.array([[float(value) for value in row[1:]]
                           for row in rows], dtype=float)
    except (ValueError, TypeError) as error:
        raise ValueError("Use YYYY-MM dates and numeric adjusted close prices") from error
    month_numbers = [date.year * 12 + date.month for date in dates]
    if len(rows) < 37 or any(b - a != 1 for a, b in
                             zip(month_numbers, month_numbers[1:])):
        raise ValueError("Need at least 37 consecutive monthly prices, oldest first")
    if not np.isfinite(prices).all() or (prices <= 0).any():
        raise ValueError("Adjusted closes must be positive and finite")
    monthly = prices[1:] / prices[:-1] - 1
    if last_36:
        monthly = monthly[-36:]
    annual_returns = monthly.mean(axis=0) * 12
    annual_covariance = np.cov(monthly, rowvar=False, ddof=1) * 12
    annual_volatilities = np.sqrt(np.diag(annual_covariance))
    if (annual_volatilities <= 0).any():
        raise ValueError("Each fund needs nonzero historical volatility")
    correlations = annual_covariance / np.outer(
        annual_volatilities, annual_volatilities
    )
    correlations = np.clip(correlations, -1.0, 1.0)
    np.fill_diagonal(correlations, 1.0)
    return (tickers, tuple(annual_returns), tuple(annual_volatilities),
            tuple(tuple(row) for row in correlations),
            (rows[-len(monthly) - 1][0], rows[-1][0], len(monthly)))


def search_five_point_mix(returns=RETURNS, volatilities=VOLATILITIES,
                          correlations=CORRELATIONS, target=RETURN_TARGET,
                          reserve_minimum=RESERVE_MINIMUM,
                          reserve_eligible=RESERVE_ELIGIBLE):
    """Try every long-only 5% mix and return the lowest-volatility feasible one."""
    count = len(returns)
    if not isfinite(target) or not isfinite(reserve_minimum) or not 0 <= reserve_minimum <= 1:
        raise ValueError("Target and reserve minimum must be finite; reserve is 0–100%")
    if count == 0:
        raise ValueError("At least one asset is required")
    portfolio_stats((1.0,) + (0.0,) * (count - 1), correlations, returns,
                    volatilities, reserve_eligible)
    covariance = np.outer(volatilities, volatilities) * np.asarray(correlations)
    if np.linalg.eigvalsh(covariance).min() < -1e-12:
        raise ValueError("Correlation inputs produce an invalid covariance matrix")

    def mixes(remaining, positions):
        if positions == 1:
            yield (remaining,)
        else:
            for units in range(remaining + 1):
                for tail in mixes(remaining - units, positions - 1):
                    yield (units, *tail)

    best = None
    for units in mixes(20, count):
        weights = tuple(value / 20 for value in units)
        expected_return, volatility, reserve_share = portfolio_stats(
            weights, correlations, returns, volatilities, reserve_eligible
        )
        if (expected_return + 1e-12 >= target
                and reserve_share + 1e-12 >= reserve_minimum
                and (best is None or volatility < best[2])):
            best = (weights, expected_return, volatility, reserve_share)
    return best


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
