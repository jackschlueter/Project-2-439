# Project 2 repository-only cold run — 2026-11-17

## Prediction before running

The local Project 2 commit `6760bd0` tracks the site bundle, mandate note, and a locked Meridian input record, but not the README, Python model, tests, bundled price panel, or raw price responses. A stranger checking out that commit should be able to read the pilot call in the site, but cannot reproduce its numeric evidence using the Python instructions because those instructions and inputs are absent. The local Git repository has no GitHub remote, so a GitHub-only proof is not yet possible.

## First check

`git archive HEAD | tar -tf -` confirmed that the commit has only `.openai/`, `dist/`, `mandate-source.md`, and `records/locked_changed_input_2026-11-17.md`. This matches the prediction. The Week 12 studio must-fix list and partner's independent cold-run result were not present in the available files, so they cannot be marked complete here.

## Fix and repeat check

Added the README, executable model and tests, 61-month price panel, raw chart responses, builder, and a one-command decision verifier in local commit `11a7e6b`. Cloned that commit into a fresh directory under `/private/tmp`, with no access to the working tree's untracked files. The clean clone:

- Rebuilt `prices.csv` from the four saved chart responses: 61 prices and 60 returns; SHA-256 `616f63cf58f37e609207c232dace8429bc864ff9b2d0b763abd1d48374f3522d`. The rebuilt file left the clone's Git working tree clean.
- Ran `verify_project2.py` using an installed Python environment with the declared dependencies. It returned **45/0/55/0**, **8.21% gross**, **8.01% net after 0.20% illustrative costs**, and **8.25% modeled volatility** for the full sample. The one-point VT reduction returned **35/0/65/0**, and the last-36-month window returned **75/0/25/0**. It printed the **PILOT** call and adoption gates.
- Ran the three named unit-test files: **7 tests passed**.

This proves the local committed source reproduces the stated numbers. The fresh clone used an existing dependency environment; a fresh dependency installation was not separately tested.

## Remaining external proof

Verify the same commit on GitHub and have the partner follow only its README from a fresh clone. Attach the Week 12 must-fix list and record each item with a file link and pass/fail result. Until those are done, this is a local reproducibility audit, not proof of the GitHub and partner handoff.

## Update 2026-11-19 — mandate switched to Meridian

**Superseded numbers:** the 45/0/55/0, 35/0/65/0, and 75/0/25/0 results above belong to the earlier young-family draft. Project 2 now uses the Lab 13 Meridian mandate only, and `verify_project2.py` reproduces the Meridian evidence instead.

**Local check, 2026-11-19:** in a fresh `.venv` (Python 3.14, `pip install -r requirements.txt`):

- `python verify_project2.py` printed equal weight FAIL (return 5.20% < 6.50%), 60/40 benchmark FAIL (reserve 0% < 3%; 95% loss 10.41% > 10%), constrained 0/20/25/55 PASS (6.51% return, 9.02% 95% loss), every stress row, and the PILOT decision with no reproduction errors.
- `python -m unittest test_portfolio_engine.py test_lab13_mandate.py test_pit_signal.py`: **9 tests passed**.
- Streamlit's headless `AppTest` rendered `app.py` with no exceptions, with the loss limit on and off.

**Still not done (needs a person):** push to a GitHub remote, then have a partner follow only the README from a fresh clone and record their result here. This file is a local reproducibility audit, not proof of the partner handoff.
