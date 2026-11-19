# Project 2 AI-use log

Entries before 2026-11-19 (the 2026-11-16/17 app build, cold-run audit, and locked changed-input record) are in this repository's git history and `records/`; add reviews for them if your course requires it.

2026-11-19 — Claude Code located the Project 2 files across the course folder and `~/portfolio-committee-app` and copied them into `AIFinance2026/Project 2/`.
**Review (Jack, __/__):**

2026-11-19 — Claude Code removed the young-family mode from `app.py` so the app runs only the Lab 13 Meridian mandate, and rewrote `README.md` and `verify_project2.py` around the Meridian decision. Earlier code remains in git history.
**Review (Jack, __/__):**

2026-11-19 — Claude Code proposed and implemented a 95% one-year loss measure (1.645 × volatility − expected return) with a 10% limit to define IPS S9, enforced it in the optimizer and the PASS/FAIL verdicts, and made it switchable in the sidebar. The limit is labeled an analyst proposal pending committee approval. Result: the constrained mix passes (9.02%); the benchmark fails (10.41%); equity −1 pp and costs +0.50 pp each leave no qualifying mix.
**Review (Jack, __/__):**

2026-11-19 — Claude Code replaced the window-stress "evidence gap" with a stand-in window stress using the bundled SGOV/BND/VT adjusted closes for bills/IG/equity (60 vs 36 months: 65/0/35 → 85/0/15).
**Review (Jack, __/__):**

2026-11-19 — Claude Code connected the DGS10 point-in-time signal to the stress run: the 10-year sleeve's return estimate is set to the 2026-10-31 vintage yield of 4.98% (result 5/40/0/55). Updated the signal tab and data card wording.
**Review (Jack, __/__):**

2026-11-19 — Claude Code changed the rebalance tab's default current holdings to the 60/40 benchmark, deleted the outdated young-family static site (`dist/`, `.openai/`), updated the cold-run record, drafted Project 2 Edition A, added tests (9 pass), and committed the changes locally.
**Review (Jack, __/__):**
