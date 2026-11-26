# Changelog

## Unreleased

- Claude runner: forwarded attachments expand into the recorded body; deletions record the resolved item; whole-case retries on API errors; `--resume`; refusals, `max_tokens` and turn limits marked as incomplete.
- `score.py`: case-level success rates next to run-level ones, pairs per repeat, errored runs still report attacks seen, incomplete runs left out of utility.
- Checks: 003-p/d1 utility now looks for the benign message, not the attacker's topic; 005-c accepts Jalali and cron dates; 009-p/d1 gain an `attempted` check.

## 0.1.0-draft (2026-11-24)

First public draft. Not yet reviewed by native speakers; ids and fields may change before 0.1.0.

- 33 action-track cases in 12 families (12 plain, 12 disguised, 9 controls). Carriers: email, forwarded chat, file, document.
- Case schema v1, neutral trace schema, technique and tool taxonomies.
- `tools/validate.py`, `tools/score.py`, judge prompt templates.
