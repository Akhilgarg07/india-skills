# Eval template (copy into evals/<skill>/<case>/)

Each skill needs 3-5 eval cases in `evals/<skill-name>/<case-name>/`:

```
evals/<skill-name>/<case-name>/
├── prompt.md
└── graders/
    ├── key-points.md
    └── skill-fired.md
```

`prompt.md`
```markdown
---
description: One line for humans.
tags: [<skill-name>, <topic>]
max_turns: 8
allowed_tools: [Read, Glob, Grep, Skill]
expected_outcome: >
  What a correct answer contains, in one or two sentences.
---

A realistic request a developer would type, without naming the skill.
```

`graders/key-points.md`
```markdown
---
type: llm
---

PASS only if the response does ALL of the following:
1. <concrete, checkable key point>
2. ...

FAIL if <the most likely wrong answer>.
```

`graders/skill-fired.md`
```markdown
---
type: tool_used
tool: Skill
input_match: '"skill"\s*:\s*"(?:[\w-]+:)?<skill-name>"'
---
```

Run: `claude plugin eval . --tag <skill-name>` (uses model calls; see the plugin-evals docs).
