# Project 2 submission manifest

Every location is a GitHub link except the videos, which are YouTube links.

Repository: https://github.com/jackschlueter/Project-2-439

## Videos

| Video | Title | Length | Link | Transcript |
|---|---|---|---|---|
| Video 1 | 439 project 2 Video 1 | 2:30 | https://youtu.be/70vq2xUNwTE | Pending |
| Video 2 | 439 project 2 Video 2 | 3:35 | https://youtu.be/9S-74I0AMUI | Pending |
| Video 3 | 439 project 2 Video 3 | 3:03 | https://youtu.be/LpSa7-WsUW0 | Pending |

Access: Videos 1, 2 and 3 are unlisted on YouTube and play without signing in (checked logged out on 2026-11-23).

## App and evidence

| Item | Link |
|---|---|
| README (run instructions, recommendation) | https://github.com/jackschlueter/Project-2-439/blob/main/README.md |
| App entry point | https://github.com/jackschlueter/Project-2-439/blob/main/app.py |
| Mandate, baselines, stress run | https://github.com/jackschlueter/Project-2-439/blob/main/lab13_mandate.py |
| One-command verifier | https://github.com/jackschlueter/Project-2-439/blob/main/verify_project2.py |
| Point-in-time signal | https://github.com/jackschlueter/Project-2-439/blob/main/pit_signal.py |
| DGS10 data card | https://github.com/jackschlueter/Project-2-439/blob/main/dgs10-data-card.md |
| Portfolio engine | https://github.com/jackschlueter/Project-2-439/blob/main/portfolio_engine.py |
| Tests | https://github.com/jackschlueter/Project-2-439/blob/main/test_lab13_mandate.py, https://github.com/jackschlueter/Project-2-439/blob/main/test_pit_signal.py, https://github.com/jackschlueter/Project-2-439/blob/main/test_portfolio_engine.py |
| Decision memo | https://github.com/jackschlueter/Project-2-439/blob/main/docs/decision-memo.md |
| Validation and AI use | https://github.com/jackschlueter/Project-2-439/blob/main/docs/validation-and-ai-use.md |
| Lab 13 and IPS sources | https://github.com/jackschlueter/Project-2-439/blob/main/lab13-source.md, https://github.com/jackschlueter/Project-2-439/blob/main/meridian-ips-source.md |
| Records (cold run, Lab 20) | https://github.com/jackschlueter/Project-2-439/tree/main/records |
| Single-file app | https://github.com/jackschlueter/Project-2-439/tree/main/single_file |
| Earlier Lab 13–15 work | https://github.com/jackschlueter/Project-2-439/tree/main/reference |

## Frozen-file checklist

Every file below is committed on `main` at https://github.com/jackschlueter/Project-2-439.

| File | Purpose | In repo |
|---|---|---|
| `README.md` | Opening AI and education statements, run instructions, recommendation | ✅ |
| `requirements.txt` | Dependencies | ✅ |
| `app.py`, `portfolio_engine.py`, `lab13_mandate.py`, `pit_signal.py`, `build_prices.py` | Runnable source | ✅ |
| `verify_project2.py`, `test_*.py` | Verifier and 9 known-answer tests | ✅ |
| `prices.csv`, `source/*.json`, `dgs10_2026-10-31.csv`, `dgs10_2026-11-03.csv` | Bundled input data | ✅ |
| `records/verify_output.txt`, `records/unittest_output.txt` | Visible executed output (2026-11-23) | ✅ |
| `docs/decision-memo.md` | Decision memo (attach to Brightspace) | ✅ |
| `docs/validation-and-ai-use.md` | Sources, tests, limitations, AI-use log, Locked Changed-Input Record (attach to Brightspace) | ✅ |
| `records/lab20_pre_run_prediction.md` | AI-off prediction, locked in commit `723d43d` before the run | ✅ |
| `records/lab20_run_result.md`, `records/lab20_baseline_output.txt`, `records/lab20_after_output.txt` | Changed-input run and outputs | ✅ |
| `records/project2_cold_run_2026-11-17.md` | Partner cold run | ✅ |
| `transcript-video-1.txt`, `transcript-video-2.txt`, `transcript-video-3.txt` | Video transcripts | Pending |
| `.env.example` | Not needed: the app uses no API keys or secrets | — |
