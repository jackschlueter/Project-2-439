"""Print the evidence behind the Project 2 committee call from bundled data."""

from pathlib import Path

from portfolio_engine import estimate, optimize, read_prices


def main():
    dates, prices = read_prices(Path(__file__).with_name("prices.csv"))
    cases = (
        ("60 months", None, 0, (.45, 0, .55, 0)),
        ("60 months, VT mean minus 1 point", None, -.01, (.35, 0, .65, 0)),
        ("last 36 months", 36, 0, (.75, 0, .25, 0)),
    )
    for label, window, adjustment, expected in cases:
        estimates = estimate(dates, prices, window)
        mix = optimize(estimates, .082, .10, adjustment)
        if mix is None or mix.weights != expected:
            raise RuntimeError(f"{label}: saved decision evidence did not reproduce")
        weights = "/".join(f"{weight:.0%}" for weight in mix.weights)
        print(f"{label}: SGOV/BND/VT/TIP {weights}; gross {mix.gross_return:.2%}; "
              f"net after 0.20% costs {mix.gross_return - .002:.2%}; "
              f"volatility {mix.volatility:.2%}; SGOV reserve {mix.reserve:.0%}")
    print("Decision: PILOT 45/0/55/0 as a research starting mix; no trade authorization.")
    print("Adoption gates: approve loss limit and SGOV reserve rule; review forward returns, costs, taxes, and liquidity.")


if __name__ == "__main__":
    main()
