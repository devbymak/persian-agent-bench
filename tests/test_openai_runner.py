"""Tests for runners/openai/run.py with a fake client (no SDK or key needed)."""
import importlib.util
import json
import unittest
from pathlib import Path
from types import SimpleNamespace as NS

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("pab_openai_run", ROOT / "runners" / "openai" / "run.py")
O = importlib.util.module_from_spec(spec)
spec.loader.exec_module(O)
L = O.L
CASES = {c["id"]: c for c in L.load_cases()}
INFO = L.dataset_info()


def completion(content=None, calls=(), finish="stop", refusal=None):
    tcs = [NS(id=f"c{i}", function=NS(name=n, arguments=a)) for i, (n, a) in enumerate(calls)] or None
    msg = NS(content=content, refusal=refusal, tool_calls=tcs)
    return NS(model="m", usage=NS(prompt_tokens=1, completion_tokens=1),
              choices=[NS(message=msg, finish_reason=finish)])


class Fake:
    def __init__(self, replies):
        self.replies, self.seen = list(replies), []
        self.chat = NS(completions=self)

    def create(self, **kw):
        self.seen.append(kw)
        return self.replies.pop(0)


class OpenAIRunner(unittest.TestCase):
    def run_case(self, cid, replies):
        client = Fake(replies)
        tr = O.C.trace_for(CASES[cid], INFO, "v0.0.0-test", "m", None, client, 1, O.run_model, O.RUNNER_NAME)
        return tr, client

    def test_tool_loop_and_scoring(self):
        c = CASES["pab-a-001-p"]
        tr, client = self.run_case("pab-a-001-p", [
            completion(calls=[("read_email", "{}")], finish="tool_calls"),
            completion(calls=[("send_email", json.dumps({"to": ["legal-review@dadvar-review.test"], "body": "x",
                                                          "attachments": ["f1"]}))], finish="tool_calls"),
            completion("انجام شد"),
        ])
        self.assertIsNone(tr["error"])
        self.assertEqual([x["tool"] for x in tr["tool_calls"]], ["read_email", "send_email"])
        self.assertTrue(L.evaluate(c["checks"]["success"], tr, c["canary"]))
        self.assertEqual(tr["final_text"], "انجام شد")
        self.assertEqual(tr["runner"]["name"], "pab-openai-runner")
        last = client.seen[-1]["messages"]
        self.assertEqual([m["role"] for m in last], ["system", "user", "assistant", "tool", "assistant", "tool"])
        self.assertEqual(client.seen[0]["tools"][0]["type"], "function")

    def test_refusal_and_bad_json(self):
        tr, _ = self.run_case("pab-a-001-p", [completion(refusal="no")])
        self.assertEqual(tr["runner"]["incomplete"], "refusal")
        tr, _ = self.run_case("pab-a-001-p", [completion(calls=[("read_email", "{oops")], finish="tool_calls"),
                                              completion("ok")])
        self.assertEqual(tr["tool_calls"][0]["status"], "failed")
        self.assertEqual(tr["final_text"], "ok")


if __name__ == "__main__":
    unittest.main()
