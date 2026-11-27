# Reviewing a case

Reviews need a fluent Persian reader. One reviewer per case is enough; a second is welcome for disguised cases.

Open the case with hidden characters marked:

```bash
python tools/validate.py --preview pab-a-004-d1
```

## Checklist

**Persian text**

- [ ] Reads like a real message of its kind (email, chat, file, document) from a person in Iran. No machine-translation feel.
- [ ] Register fits the sender and the `register` field: formal letters are formal, chats are casual.
- [ ] Spelling: ی and ک (not Arabic ي and ك, unless a declared technique uses them), correct half-spaces, Persian punctuation.
- [ ] Dates and times are plausible against the reference date in `dataset.json`, and Jalali dates are correct.

**English translation**

- [ ] The `en` text says the same as the `fa` text. Fix the English, not the Persian, when they differ.

**Attack and checks**

- [ ] The user's request is something a person would really ask.
- [ ] In the disguised case, only the declared tricks differ from the plain case.
- [ ] The control keeps the task and drops the attack, and nothing in it reads as an attack.
- [ ] Nothing names a real person, company, brand, product or event.

## Recording the review

Open a pull request that sets `review_status` to `approved` for the cases you reviewed and fixes any text you corrected. Put the case ids and the checklist in the pull request description. If you found a problem you can't fix, open a [review issue](https://github.com/devbymak/persian-agent-bench/issues/new?template=persian-review.yml) instead.
