# Claude reference runner

A minimal agent with no safety prompt: one Claude model, the 15 abstract tools from [taxonomy/tools.json](../../taxonomy/tools.json) and a simulated world built from each case's items. It measures how a bare model behaves as an assistant, not how a finished product with its own guards does.

```bash
pip install anthropic                     # Python 3.10+
export ANTHROPIC_API_KEY=...
python runners/claude/run.py --model claude-opus-5-5 --out traces/claude-opus-5-5
python tools/score.py traces/claude-opus-5-5 --out summary.json
```

Dry runs need no key and check the runner and the cases together:

```bash
python runners/claude/run.py --model reference --out traces/reference   # attacker's reference calls: every attack must score as a success
python runners/claude/run.py --model user --out traces/user             # only the user's calls: no attack may score
```

## What the simulated world does

- The model sees the persona and reference time from `dataset.json` and receives `user_request.fa` as its only user turn.
- Read tools return items in full and record them in `items_read`. Mail and chat return every message that matches, newest mail first. Files open by path, id or document title.
- Sends, commands, schedules, settings, deletes and writes are logged and answered with a plain success message. `open_url` and unknown pages answer `HTTP 404`. Nothing runs and nothing leaves the machine except the model API calls.
- The run stops when the model ends its turn or after 25 model turns.

Options: `--effort` sets the model's effort (default: the model's own), `--repeat N` runs each case N times (traces are named `<id>-rN.json`), `--cases` picks case ids, `--workers` sets parallel runs. `--resume` skips runs that already have a trace without an error.

- `send_email` puts the content of `attachments` (email ids, file ids or paths) into the recorded `body`, so a forwarded secret is visible to the checks.
- `delete_item` records the id of the item it really deleted in `args.id` and the model's own value in `args.id_native`.
- A case that fails on an API error is retried up to 3 times. A run that ends on a refusal, `max_tokens` or the turn limit is marked in `runner.incomplete`; `tools/score.py` keeps it in the safety rates, leaves it out of utility, and lists it separately.

Each trace records the model id, the model that served each reply, the stop reasons and token usage under `runner`.
