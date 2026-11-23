"""Print the evidence behind the Meridian Project 2 committee call."""

from lab13_mandate import (BENCHMARK, CORR, EQUAL_WEIGHT, LOSS_LIMIT, MEANS, VOL, loss95, mandate_verdict,
                           proxy_window, search, signal_yield, stats, weight_text)

HURDLE, RESERVE = .065, .03


def show(label, weights, figures):
    gross, vol, reserve = figures
    verdict, reasons = mandate_verdict(weights, gross, reserve, HURDLE, RESERVE, vol, LOSS_LIMIT)
    print(f"{label}: {weight_text(weights)}; return {gross:.2%}; volatility {vol:.2%}; "
          f"95% loss {loss95(gross, vol):.2%}; eligible reserve {reserve:.0%}; "
          f"{verdict} ({'; '.join(reasons)})")


def check(label, answer, expected):
    if expected is None:
        if answer is not None:
            raise RuntimeError(f"{label}: expected no qualifying mix")
        print(f"{label}: STOP, no qualifying mix")
        return
    if answer is None or answer[0] != expected:
        raise RuntimeError(f"{label}: saved decision evidence did not reproduce")
    print(f"{label}: {answer[0]}; return {answer[1]:.2%}; volatility {answer[2]:.2%}; "
          f"95% loss {loss95(answer[1], answer[2]):.2%}")


def main():
    print("Inputs (Lab 13 course training values, not market estimates; sleeves bills/10-year/IG/equity):")
    print(f"  Expected returns {' / '.join(f'{m:.2%}' for m in MEANS)}; volatilities {' / '.join(f'{v:.2%}' for v in VOL)}")
    print(f"  Correlations: 10-year/IG {CORR[1, 2]:.2f}, IG/equity {CORR[2, 3]:.2f}, 10-year/equity {CORR[1, 3]:.2f}, bills/10-year {CORR[0, 1]:.2f}")
    print(f"  Mandate: {HURDLE:.1%} gross return hurdle (2.5% CPI + 4.0 pp); {RESERVE:.0%} eligible reserve floor (bills and 10-year only); "
          f"proposed {LOSS_LIMIT:.0%} 95% one-year loss limit; long-only 5% grid")
    print("As of: DGS10 ALFRED vintage 2026-10-31 (signal stress); SGOV/BND/VT month-end prices Sep 2021-Sep 2026 (window stress)\n")
    show("Equal weight", EQUAL_WEIGHT, stats(EQUAL_WEIGHT))
    show("60/40 benchmark", BENCHMARK, stats(BENCHMARK))
    base = search(HURDLE, RESERVE, loss_limit=LOSS_LIMIT)
    show("Constrained portfolio", base[0], base[1:])
    print("\nStress run (proposed 10% loss limit enforced; weights are bills/10-year/IG/equity):")
    check("Estimate: equity mean -1 pp", search(HURDLE, RESERVE, -.01, loss_limit=LOSS_LIMIT), None)
    check("Estimate: equity mean -1 pp, no loss limit", search(HURDLE, RESERVE, -.01), (0, .10, .10, .80))
    corr = CORR.copy()
    corr[2, 3] = corr[3, 2] = .50
    check("Estimate: IG-equity correlation 0.50", search(HURDLE, RESERVE, correlation=corr,
                                                         loss_limit=LOSS_LIMIT), (0, .40, 0, .60))
    check("Window: 60 months, SGOV/BND/VT stand-ins", proxy_window(None, HURDLE, RESERVE, LOSS_LIMIT), (.65, 0, .35))
    check("Window: 36 months, SGOV/BND/VT stand-ins", proxy_window(36, HURDLE, RESERVE, LOSS_LIMIT), (.85, 0, .15))
    check("Costs: +0.50 pp", search(HURDLE + .005, RESERVE, loss_limit=LOSS_LIMIT), None)
    if search(HURDLE, .40, loss_limit=LOSS_LIMIT) is None or search(HURDLE, .45, loss_limit=LOSS_LIMIT):
        raise RuntimeError("Constraint breakpoint did not reproduce")
    print("Constraint: reserve floor 45% is the first infeasible 5% step (breakpoint, not policy)")
    day, value = signal_yield()
    check(f"Signal: 10-year estimate = DGS10 {value:.2f}% ({day})",
          search(HURDLE, RESERVE, loss_limit=LOSS_LIMIT, ten_year_return=value / 100), (.05, .40, 0, .55))
    print("\nDecision: PILOT the process; no allocation or trade authorization.")
    print("Stop condition triggered: equity -1 pp and costs +0.50 pp each leave no mix meeting the return, reserve, and loss rules.")
    print("Adoption gates: committee approves the loss limit; verify liquidity and issuer exposure; replace training estimates with dated forward estimates.")
    print("Reject if: realistic validated assumptions repeatedly trigger the stop condition, or liquidity requirements cannot be met.")
    print("Committee ask: approve the pilot as a research process with no capital allocation, and take on the three adoption gates.")


if __name__ == "__main__":
    main()
