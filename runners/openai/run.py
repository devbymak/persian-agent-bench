#!/usr/bin/env python3
"""Reference runner for OpenAI models: same simulated world, tools, prompt and
trace format as runners/claude/run.py, with the OpenAI Responses API.

  pip install openai
  export OPENAI_API_KEY=...
  python runners/openai/run.py --model <model id> --repeat 3 --out traces/<model id>
  python tools/score.py traces/<model id> --out summary.json

`--list-models` prints the model ids your key can use.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("pab_claude_runner", ROOT / "runners" / "claude" / "run.py")
C = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(C)
L = C.L

RUNNER_NAME = "pab-openai-runner"


def tool_defs() -> list[dict]:
    return [{"type": "function", "name": t["name"], "description": t["description"],
             "parameters": t["input_schema"]} for t in C.tool_defs()]


def _dump(item) -> dict:
    return item.model_dump(exclude_none=True, by_alias=True) if hasattr(item, "model_dump") else dict(vars(item))


def run_model(client, model: str, effort: str | None, case: dict, info: dict, world, runner: dict) -> str:
    # Responses API: reasoning models accept function tools only here, not in Chat Completions.
    # store=False keeps runs out of OpenAI's stored responses; reasoning is carried forward encrypted.
    items = [{"role": "user", "content": case["user_request"]["fa"]}]
    texts, stops, usage = [], [], {"input_tokens": 0, "output_tokens": 0}
    params = {"model": model, "instructions": C.system_prompt(info), "tools": tool_defs(),
              "max_output_tokens": 16000, "store": False, "include": ["reasoning.encrypted_content"]}
    if effort:
        params["reasoning"] = {"effort": effort}
    for _ in range(C.MAX_TURNS):
        resp = client.responses.create(input=items, **params)
        if resp.usage:
            usage["input_tokens"] += resp.usage.input_tokens or 0
            usage["output_tokens"] += resp.usage.output_tokens or 0
        runner["served_model"] = resp.model
        stops.append(resp.status)
        out = list(resp.output or [])
        refused = [c for o in out if o.type == "message" for c in o.content if c.type == "refusal"]
        if refused:
            runner["incomplete"] = "refusal"
            break  # the refused message is not shown as an answer
        if resp.status == "incomplete":
            reason = getattr(resp.incomplete_details, "reason", None)
            runner["incomplete"] = "refusal:content_filter" if reason == "content_filter" else "max_tokens"
            texts += [c.text.strip() for o in out if o.type == "message" for c in o.content
                      if c.type == "output_text" and c.text.strip()]
            break
        texts += [c.text.strip() for o in out if o.type == "message" for c in o.content
                  if c.type == "output_text" and c.text.strip()]
        calls = [o for o in out if o.type == "function_call"]
        if not calls:
            break
        items += [_dump(o) for o in out]
        for tc in calls:
            try:
                args = json.loads(tc.arguments or "{}")
                if not isinstance(args, dict):
                    raise ValueError("arguments are not an object")
            except ValueError as e:
                world.calls.append({"seq": len(world.calls) + 1, "phase": "attack",
                                    "tool": tc.name if tc.name in C.DESCRIPTIONS else None,
                                    "native_tool": tc.name, "args": {"_raw": tc.arguments or ""},
                                    "status": "failed", "origin": "agent"})
                result = f"Error: invalid JSON arguments ({e})."
            else:
                result, _err = world.call(tc.name, args)
            items.append({"type": "function_call_output", "call_id": tc.call_id, "output": result})
    else:
        stops.append("max_turns")
        runner["incomplete"] = "max_turns"
    runner["stop_reasons"], runner["usage"] = stops, usage
    return "\n\n".join(texts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", help="OpenAI model id")
    ap.add_argument("--out")
    ap.add_argument("--effort", choices=["none", "minimal", "low", "medium", "high", "xhigh", "max"],
                    help="reasoning effort (default: the model's own)")
    ap.add_argument("--cases", nargs="*", help="case ids (default: all active)")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--repeat", type=int, default=1, help="runs per case; traces are named <id>-rN.json")
    ap.add_argument("--resume", action="store_true", help="skip runs whose trace exists without an error")
    ap.add_argument("--list-models", action="store_true")
    a = ap.parse_args()

    import openai
    client = openai.OpenAI(max_retries=6)
    if a.list_models:
        for m in sorted(m.id for m in client.models.list()):
            print(m)
        return
    if not a.model or not a.out:
        ap.error("--model and --out are required")

    ref = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip() or "unknown"
    info = L.dataset_info()
    cases = [c for c in L.load_cases() if c.get("status") == "active" and (not a.cases or c["id"] in a.cases)]
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)

    def name_of(c, r):
        return f"{c['id']}-r{r + 1}.json"

    def done(c, r):
        p = out / name_of(c, r)
        if not (a.resume and p.exists()):
            return False
        try:
            return not json.loads(p.read_text(encoding="utf-8")).get("error")
        except ValueError:
            return False

    jobs = [(c, r) for c in cases for r in range(a.repeat) if not done(c, r)]
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        futs = {ex.submit(C.trace_for, c, info, ref, a.model, a.effort, client, r + 1, run_model, RUNNER_NAME): (c, r)
                for c, r in jobs}
        for f in as_completed(futs):
            c, r = futs[f]
            tr = f.result()
            name = name_of(c, r)
            (out / name).write_text(json.dumps(tr, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
            print(f"{name}: calls={[x['native_tool'] for x in tr['tool_calls']]} error={tr['error']}"
                  f" incomplete={tr['runner'].get('incomplete')}", flush=True)
    print(f"done: {len(jobs)} runs in {time.time() - t0:.0f}s -> {out}")


if __name__ == "__main__":
    main()
