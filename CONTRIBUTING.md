# Contributing to india-skills

Thanks for helping AI agents get India right. Accuracy is the whole point of this repo, so please
read the rules below before opening a PR.

## Ground rules

1. **Official sources only for facts.** Rates, thresholds, formats, deadlines and API parameters must
   come from an official source: CBIC / GST portal / GST Council, Income Tax Department
   (incometax.gov.in, incometaxindia.gov.in), MCA, RBI, NPCI, UIDAI, MeitY, India Post, PIB, the
   Gazette of India, or the vendor's own docs/SDK (e.g. Razorpay). Blogs and aggregators can point you
   to a source, but they are not the source.
2. **Cite everything** in `skills/<skill>/references/sources.md`: URL, what fact it supports, and how
   you checked it (`[page]` read the official page/PDF, `[extract]` search-engine extract of an official
   URL, `[mirror]` official document from a third-party copy, `[test]` observed by running code,
   `[reported]` news reports of an official circular). Update the `Last verified: YYYY-MM-DD` line.
3. **Never guess.** If you can't verify something, write `TODO(verify): <what and why>` instead.
   `python3 tools/check_skills.py --todos` lists them all; please also update [VERIFY.md](VERIFY.md).
4. **Tax/legal skills carry a disclaimer** ("Not tax advice" / "Not legal advice", and that rules change
   with Union Budgets / GST Council decisions). The linter enforces this for the skills listed in
   `NEEDS_DISCLAIMER` in `tools/check_skills.py`.
5. **No personal data.** Use synthetic values in tests and docs (generate Aadhaar test numbers with a
   Verhoeff check digit; synthetic GSTINs with a valid check character). Published business GSTINs are
   fine for checksum test vectors; never use individuals' PAN/Aadhaar/phone numbers.

## Adding a skill

1. Copy the template: `cp -r _template skills/<your-skill-name>`
   - The name must be 1-64 chars of lowercase letters, digits and single hyphens, and must equal the
     folder name (Agent Skills spec).
2. Edit `SKILL.md`:
   - Frontmatter uses only spec fields: `name`, `description` (≤ 1024 chars), `license`, `metadata`
     (and optionally `compatibility`, `allowed-tools`).
   - The `description` must say **what** the skill does **and when** to use it (task types, file types,
     keywords). This is how agents decide to load it.
   - Keep `SKILL.md` **under 300 lines**. Put long tables, full rule text and examples in `references/`
     and link them with relative paths (one level deep).
3. Scripts go in `scripts/`:
   - **Python 3 standard library only**, no third-party dependencies.
   - Work as **both a CLI and an importable module**. Exit code 0 = success/valid, 1 = invalid,
     2 = usage error. Support `--json` where output is structured.
   - Use `decimal.Decimal` (or integer paise) for money; never binary floats.
   - Never print, log or accept via argv sensitive identifiers (read Aadhaar etc. from stdin; secrets
     from environment variables).
   - If you need a script from another skill, copy it and add a test asserting the copies are identical
     (see `tests/test_gst_invoicing.py`).
4. Tests go in `tests/test_<skill_name_with_underscores>.py`:
   - Load scripts with `from conftest import load_script` (they are not a package).
   - Cover known-valid and known-invalid values, edge cases, and the CLI.
5. Evals go in `evals/<skill>/<case>/` (3-5 cases), in the `claude plugin eval` format:
   - `prompt.md`: frontmatter (`description`, `tags`, `max_turns`, `allowed_tools`, `expected_outcome`)
     and a realistic user prompt in the body.
   - `graders/key-points.md`: `type: llm` rubric with concrete PASS/FAIL conditions (the key points a
     correct answer must include).
   - `graders/skill-fired.md`: `type: tool_used`, `tool: Skill`, `input_match` on your skill name.
6. Add the skill to the table in `README.md` and to `CHANGELOG.md`.

## Before you open a PR

```bash
python3 -m pip install pytest
pytest                                   # all script tests
python3 tools/check_skills.py --todos    # spec + repo-rule lint, lists TODO(verify)
claude plugin validate --strict .        # optional, if you have Claude Code installed
claude plugin eval . --tag <your-skill> --runs 1 --ablation none   # optional, uses model calls
```

CI runs `pytest` and `tools/check_skills.py` on every push and PR.

## Updating an existing rule

- Change the fact, the script/test that encodes it, and `sources.md` (new URL and date) in the same PR.
- Keep historical rules when old data still uses them (e.g. GST rates before 22 Sep 2025; TDS sections
  of the 1961 Act for payments up to 31 Mar 2026). Add effective dates rather than deleting history.
