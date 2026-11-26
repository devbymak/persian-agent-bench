# Changelog

## Unreleased

- Gated Hugging Face copy of the 0.1.0 cases, linked from the README.

## 0.1.0 (2026-11-26)

First release. Case ids and fields are now stable within 0.1.x.


- Runner 0.3.0: a small simulated shell for `run_command`; cases 008-p/d1/c gain the Makefile and requirements.txt their README names (008-c failed for some models because they were missing).
- First results: six models, 3 runs per case, in `results/2026-11` and the README.
- `score.py` reports refusals and task completion over all attack runs.
- OpenAI reference runner in `runners/openai`.
- Claude runner: forwarded attachments expand into the recorded body; deletions record the resolved item; whole-case retries on API errors; `--resume`; refusals, `max_tokens` and turn limits marked as incomplete.
- `score.py`: case-level success rates next to run-level ones, pairs per repeat, errored runs still report attacks seen, incomplete runs left out of utility.
- Checks: 003-p/d1 utility now looks for the benign message, not the attacker's topic; 005-c accepts Jalali and cron dates; 009-p/d1 gain an `attempted` check.

## 0.1.0-draft (2026-11-24)

First public draft. Not yet reviewed by native speakers; ids and fields may change before 0.1.0.

- 33 action-track cases in 12 families (12 plain, 12 disguised, 9 controls). Carriers: email, forwarded chat, file, document.
- Case schema v1, neutral trace schema, technique and tool taxonomies.
- `tools/validate.py`, `tools/score.py`, judge prompt templates.
