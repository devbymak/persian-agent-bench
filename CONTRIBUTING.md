# Contributing

Thanks for helping. The set needs three things most:

1. **Native-speaker review** of the Persian in existing cases. See [docs/review.md](docs/review.md).
2. **New attack families**, especially harder ones. Version 0.1 is too easy for current models: only one family ever worked (see [results](results/2026-11/README.md)).
3. **Runners and results** for other agents and harnesses. See [docs/runner-guide.md](docs/runner-guide.md).

Report anything harmful in a case (a real person, a real brand, a payload that could do damage) privately, as described in [SECURITY.md](SECURITY.md), not in a public issue.

## Propose a new attack family

You can start with an idea or with finished files.

- **Idea only:** open a [new case issue](https://github.com/devbymak/persian-agent-bench/issues/new?template=new-case.yml). Describe the attack in English; Persian text is welcome but optional. Someone can turn it into files.
- **Finished files:** open a pull request with one family: a plain case (`-p`), a disguised case (`-d1`) and a control (`-c`).

### Writing the files

1. Read [docs/authoring.md](docs/authoring.md). Its rules are not optional: invented people and companies, reserved hosts and addresses only, numbers that are invalid by construction, no working payloads, no real-world harm topics.
2. Copy an existing family in `cases/action/` that is close to yours and use the next free family number. Keep the three files consistent: the plain and disguised cases differ only in the declared Persian tricks (`techniques`), and the control keeps the same task without the attack.
3. Put the canary only in a private item, and the injection text exactly once in the carrier.
4. Write `checks` that fire on the attacker's action and stay quiet when the agent only does the user's task. Fill `user_calls` with the calls an agent makes to do the task, so the validator can test that.
5. Set `review_status` to `draft`.
6. Run:

```bash
python tools/validate.py --format          # canonical formatting, hidden characters as \uXXXX
python tools/validate.py                   # every rule; must show 0 errors
python tools/validate.py --preview pab-a-013-d1   # read your case with hidden characters marked
python -m unittest discover -s tests
python runners/claude/run.py --model reference --cases pab-a-013-p pab-a-013-d1 pab-a-013-c --out /tmp/ref
python runners/claude/run.py --model user --cases pab-a-013-p pab-a-013-d1 pab-a-013-c --out /tmp/user
python tools/score.py /tmp/ref             # the attack must count as worked
python tools/score.py /tmp/user            # the attack must not count
```

The two dry runs need no API key: `reference` replays `user_calls` plus the attacker's calls, and `user` replays only `user_calls`. They write no reply text, so task checks that read the reply show as not done; that is expected.

GitHub runs the validator and the tests on every pull request.

### What makes an attack worth adding

- It targets a realistic task: the user asks for something ordinary and the attack rides on content the agent reads for that task.
- It is new: a different hiding place, goal or approach from the existing families, not a reworded copy.
- Its plain and disguised versions isolate one Persian trick, so the pair shows what the trick adds.

## Review and release

A case moves from `draft` to `in_review` once its pull request is merged, and to `approved` after a native speaker has checked it with [docs/review.md](docs/review.md). Releases are cut with `python tools/validate.py --release`, which requires every active case to be `approved`.

## License

By contributing you agree that case files are released under CC BY 4.0 ([LICENSE-DATA](LICENSE-DATA)) and code under MIT ([LICENSE](LICENSE)). Write the text yourself; never copy from other datasets or from real messages.
