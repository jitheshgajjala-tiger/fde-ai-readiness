# Assignment 3: Packaging a skill

**Section:** 1. Agentic AI Coding Assistants (GitHub Copilot and Claude Code)

Take a process you've explained to a teammate more than once (e.g., how to validate an STTM file) and turn it into a `SKILL.md` with clear trigger conditions and step-by-step instructions. Test that the assistant picks it up automatically when you describe the task in natural language, without naming the skill.

## Deliverables

- [x] Approach and steps taken
- [x] Evidence (screenshots, output, or links)
- [x] Result and what I learned
- [ ] Test auto-pickup: in a fresh Copilot Chat, ask in plain words (without naming the skill) and record whether it loaded (not done yet)

## Approach

**Process packaged:** validating an STTM document, which I would otherwise explain by hand each time.

Files in `.github/skills/validate-sttm/`:
- `SKILL.md`: a trigger-rich `description` (check, review, QA, sign off an STTM or mapping doc), when to use and not use it, numbered steps, and a table explaining each check.
- `validate_sttm.py`: a helper script with 6 checks (title, target table, load schedule, source are `FAIL`; column rules and reject handling are `WARN`). It exits with code 1 on any `FAIL` and follows the repo conventions (logging, errors naming the source).

## Evidence

Run on the three sample STTM files:

```
customers_sttm.md: title=PASS, target_table=PASS, load_schedule=PASS, source=PASS, column_rules=PASS, reject_handling=WARN
orders_sttm.md:    title=PASS, target_table=PASS, load_schedule=PASS, source=PASS, column_rules=PASS, reject_handling=PASS
products_sttm.md:  title=PASS, target_table=PASS, load_schedule=PASS, source=PASS, column_rules=PASS, reject_handling=PASS
exit code 0
```

Negative test on a non-STTM file (`dq_rules.md`):

```
dq_rules.md: title=FAIL, target_table=PASS, load_schedule=FAIL, source=FAIL, column_rules=WARN, reject_handling=PASS
exit code 1
```

## Result and what I learned

- The script finds a real gap: the customers STTM says nothing about rejected or quarantined rows.
- The script proves the checks can both pass and fail, since the non-STTM file fails.
- The checks are regex patterns for this repo's prose style. A table-style STTM would need different patterns, so the skill is only as general as its checks.
- The `description` line is what decides whether the assistant picks the skill, so it lists the phrases a user would actually type.
- **Not yet proven:** automatic pickup. I could not test it, because a skill added during a session is not visible to that session. Reload the window, start a fresh chat, type something like "is the orders mapping doc complete before I hand it over?", and check whether the skill is read. Record the result here.

## Notes

