# OpenAI reference runner

Same simulated world, tools, system prompt, user turn and trace format as the [Claude runner](../claude/README.md), so results compare directly. It uses the OpenAI Chat Completions API with function calling.

```bash
pip install openai
export OPENAI_API_KEY=...
python runners/openai/run.py --list-models                      # ids your key can use
python runners/openai/run.py --model <id> --repeat 3 --out traces/<id>
python tools/score.py traces/<id> --out summary.json
```

`--effort` sets `reasoning_effort` (default: the model's own). A refusal or a content filter stop is marked in `runner.incomplete`, as is a reply cut off by the token limit. Arguments that are not valid JSON are recorded as a failed call and the model is told so.
