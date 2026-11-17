"""Small, deterministic portfolio model for the committee app."""

import csv
from dataclasses import dataclass
from io import StringIO
from itertools import product
from math import isfinite, sqrt
from pathlib import Path

import numpy as np

FUNDS = ("SGOV", "BND", "VT", "TIP")


@dataclass(frozen=True)
class Estimates:
    mean: np.ndarray
    covariance: np.ndarray
    start: str
    end: str
    months: int


@dataclass(frozen=True)
class Mix:
    weights: tuple[float, ...]
    gross_return: float
    volatility: float
    reserve: float


def read_prices(source: str | Path | bytes) -> tuple[list[str], np.ndarray]:
    """Read a consecutive YYYY-MM adjusted-close panel in fixed fund order."""
    if isinstance(source, bytes):
        raw = source.decode("utf-8-sig")
    else:
        raw = Path(source).read_text(encoding="utf-8-sig")
    rows = list(csv.reader(StringIO(raw)))
    if not rows or tuple(rows[0]) != ("Month", *FUNDS):
        raise ValueError("CSV columns must be Month,SGOV,BND,VT,TIP in that order.")
    if len(rows) < 38 or any(len(row) != 5 for row in rows[1:]):
        raise ValueError("At least 37 monthly prices with four complete fund columns are required.")
    dates = [row[0] for row in rows[1:]]
    try:
        from datetime import datetime
        month_ids = [d.year * 12 + d.month for d in (datetime.strptime(x, "%Y-%m") for x in dates)]
        prices = np.array([[float(x) for x in row[1:]] for row in rows[1:]], dtype=float)
    except ValueError as exc:
        raise ValueError("Dates must be YYYY-MM and prices must be numeric.") from exc
    if any(b - a != 1 for a, b in zip(month_ids, month_ids[1:])):
        raise ValueError("Prices must be in consecutive months, oldest first.")
    if not np.isfinite(prices).all() or (prices <= 0).any():
        raise ValueError("Prices must be positive and finite.")
    return dates, prices


def estimate(dates: list[str], prices: np.ndarray, months: int | None = None) -> Estimates:
    monthly = prices[1:] / prices[:-1] - 1
    if months is not None:
        if months < 24 or months > len(monthly):
            raise ValueError("Return window must contain 24 or more months within the panel.")
        monthly = monthly[-months:]
    mean = monthly.mean(axis=0) * 12
    covariance = np.cov(monthly, rowvar=False, ddof=1) * 12
    return Estimates(mean, covariance, dates[-len(monthly) - 1], dates[-1], len(monthly))


def score(weights, mean, covariance) -> Mix:
    weights = tuple(float(x) for x in weights)
    w = np.array(weights)
    return Mix(weights, float(w @ mean), sqrt(max(0.0, float(w @ covariance @ w))), weights[0])


def optimize(estimates: Estimates, gross_floor: float, reserve_floor: float,
             vt_adjustment: float = 0.0) -> Mix | None:
    """Choose least volatile qualifying long-only mix on a 5% grid."""
    if not all(isfinite(x) for x in (gross_floor, reserve_floor, vt_adjustment)):
        raise ValueError("Settings must be finite.")
    if not 0 <= reserve_floor <= 1:
        raise ValueError("Reserve floor must be between 0% and 100%.")
    mean = estimates.mean.copy()
    mean[2] += vt_adjustment
    best = None
    for a, b, c in product(range(21), repeat=3):
        d = 20 - a - b - c
        if d < 0 or a / 20 + 1e-12 < reserve_floor:
            continue
        candidate = score((a / 20, b / 20, c / 20, d / 20), mean, estimates.covariance)
        if candidate.gross_return + 1e-12 < gross_floor:
            continue
        if best is None or candidate.volatility < best.volatility:
            best = candidate
    return best


def rebalance(current: tuple[float, ...], target: tuple[float, ...], value: float):
    if len(current) != 4 or any(not isfinite(x) or x < 0 for x in current):
        raise ValueError("Current holdings must be four nonnegative weights.")
    if abs(sum(current) - 1) > 1e-6 or not isfinite(value) or value <= 0:
        raise ValueError("Current weights must total 100% and portfolio value must be positive.")
    changes = tuple((t - c) * value for c, t in zip(current, target))
    turnover = sum(abs(x) for x in changes) / (2 * value)
    return changes, turnover
