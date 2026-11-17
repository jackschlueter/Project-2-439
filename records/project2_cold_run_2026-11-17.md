# Project 2 repository-only cold run — 2026-11-17

## Prediction before running

The local Project 2 commit `6760bd0` tracks the site bundle, mandate note, and a locked Meridian input record, but not the README, Python model, tests, bundled price panel, or raw price responses. A stranger checking out that commit should be able to read the pilot call in the site, but cannot reproduce its numeric evidence using the Python instructions because those instructions and inputs are absent. The local Git repository has no GitHub remote, so a GitHub-only proof is not yet possible.

## First check

`git archive HEAD | tar -tf -` confirmed that the commit has only `.openai/`, `dist/`, `mandate-source.md`, and `records/locked_changed_input_2026-11-17.md`. This matches the prediction. The Week 12 studio must-fix list and partner's independent cold-run result were not present in the available files, so they cannot be marked complete here.

## Fix and repeat check

Add the README, executable model and tests, 61-month price panel, raw chart responses, builder, and a one-command decision verifier to the Git repository. Then check out the new commit to a separate clean directory, rebuild the price panel, run the verifier and tests, and compare the output to the stated call. Record the commit and exact result below after that run.

## Remaining external proof

Verify the same commit on GitHub and have the partner follow only its README from a fresh clone. Attach the Week 12 must-fix list and record each item with a file link and pass/fail result. Until those are done, this is a local reproducibility audit, not proof of the GitHub and partner handoff.
