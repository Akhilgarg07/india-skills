---
name: your-skill-name
description: One or two sentences saying WHAT this skill does and WHEN an agent should use it - name the tasks (e.g. "writing invoice generators", "reviewing payment webhooks"), file types, libraries and keywords a user's request would contain. Max 1024 characters. Rename the folder to match `name` (lowercase letters, digits, single hyphens).
license: MIT
metadata:
  version: "0.1.0"
  last-verified: "YYYY-MM-DD"
---

# Your skill title

> **Not tax/legal advice.** (Keep this line for tax or legal topics, and say that rules change with
> Union Budgets / GST Council decisions / regulator circulars. Delete it otherwise.)

One short paragraph: the problem this skill solves and the mistakes agents usually make without it.

## Quick reference

| Thing | Rule | Source |
|---|---|---|
| ... | ... | see references/sources.md |

## Rules

1. The most important rule, stated as an instruction ("Always ...", "Never ...").
2. ...

Mark anything you couldn't confirm from an official source as `TODO(verify): ...`.

## Workflow (if the task has steps)

1. ...
2. ...

## Script

```bash
python3 scripts/example_tool.py VALUE           # what it prints
python3 scripts/example_tool.py --json VALUE
```
Module: `validate(value) -> dict`.

## More detail

- Long tables and full rule text: [references/details.md](references/details.md)
- Sources and verification dates: [references/sources.md](references/sources.md)

Keep this file under 300 lines.
