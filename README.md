# india-skills

**Agent Skills that teach AI coding agents to get Indian tax, payment, ID and formatting
details right: GST, TDS, UPI, Razorpay, GSTIN/PAN/Aadhaar, lakh/crore, DPDP and the
April-March financial year.**

[![CI](https://github.com/akhilgarg07/india-skills/actions/workflows/ci.yml/badge.svg)](https://github.com/akhilgarg07/india-skills/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Agent Skills](https://img.shields.io/badge/Agent%20Skills-10-orange)

<!-- DEMO GIF: record Claude Code generating a GST invoice with and without the plugin, save it as
     docs/demo.gif, and replace the line below with:
     <p align="center"><img src="docs/demo.gif" alt="Demo: GST invoice with india-skills" width="720"></p> -->
> 🎬 **Demo GIF coming soon:** Claude Code generating a GST invoice, with and without india-skills.

## Why this exists

AI coding agents are trained mostly on Western code. Ask one to build something for India and you
often get answers that look plausible but are wrong:

- a GSTIN regex that rejects real GSTINs and never checks the check character;
- GST slabs of 5/12/18/28% in 2026 (they were rationalised to 5/18/40% on 22 Sep 2025);
- 18% applied to a tax-inclusive price (₹1,18,000 × 18% instead of ₹1,18,000 × 18/118);
- `194C` quoted for a TDS payment after 1 April 2026 (it is now s.393 of the Income-tax Act 2025);
- Aadhaar numbers logged in plain text, or "validated" with a 12-digit regex;
- `1,234,567` instead of `12,34,567`, and "one million two hundred thousand" instead of
  "Twelve Lakh";
- `new Date("01/04/2026")` read as 4 January, and FY reports bucketed on UTC dates.

Each skill in this repo is a small, focused folder of instructions, reference tables and
**stdlib-only Python helpers**. Agents load a skill only when a task needs it. Every factual rule is
taken from an official source (CBIC/GST Council, Income Tax Department, RBI, NPCI, UIDAI, MeitY,
India Post, Razorpay docs) and cited in the skill's `references/sources.md` with a last-verified date.
Anything that couldn't be verified is marked `TODO(verify)` instead of guessed.

## Skills

| Skill | What it gets right |
|---|---|
| [`gst-invoicing`](skills/gst-invoicing/SKILL.md) | Rule 46 invoice fields, 16-char numbering per FY, CGST+SGST/UTGST vs IGST from place of supply, HSN/SAC digits, exports/SEZ, e-invoicing (IRN/QR, ₹5 crore, 30-day rule) |
| [`gst-tax-calculation`](skills/gst-tax-calculation/SKILL.md) | Current 5/18/40% structure (and 0.25/1.5/3%), inclusive vs exclusive, paise and s.170 rupee rounding, reverse charge |
| [`tds-basics`](skills/tds-basics/SKILL.md) | Salary, contractor and professional-fee TDS, thresholds, no-PAN 20%, GST exclusion, 1961 → 2025 Act section mapping |
| [`indian-id-validation`](skills/indian-id-validation/SKILL.md) | GSTIN (mod-36 check char), PAN, TAN, IFSC, mobile, PIN, Aadhaar (Verhoeff + strict masking/no-storage rules) |
| [`upi-payments`](skills/upi-payments/SKILL.md) | `upi://pay` parameters per NPCI spec, static vs dynamic QR, VPA checks, server-side payment status, end of P2P collect |
| [`razorpay-integration`](skills/razorpay-integration/SKILL.md) | Orders in paise, signature verification with the stored order id, raw-body webhook HMAC, event de-duplication, idempotent refunds |
| [`indian-number-formatting`](skills/indian-number-formatting/SKILL.md) | Lakh/crore grouping, ₹ (U+20B9), `Intl.NumberFormat('en-IN')` pitfalls, amount in words ("One Lakh Twenty Thousand Rupees Only") |
| [`indian-addresses`](skills/indian-addresses/SKILL.md) | Address form design, 28 States + 8 UTs with GST codes, PIN structure (circles are not states), DIGIPIN |
| [`dpdp-privacy`](skills/dpdp-privacy/SKILL.md) | DPDP Act 2023 + Rules 2025 checklist: phased dates, consent/notice, erasure, 72-hour Board report, 90-day rights, children |
| [`indian-dates-and-fiscal-year`](skills/indian-dates-and-fiscal-year/SKILL.md) | April-March FY and quarters, AY vs "tax year", IST (UTC+05:30), strict DD/MM/YYYY, `en-IN` date pitfalls |

## Install

### Claude Code (plugin)

```text
/plugin marketplace add akhilgarg07/india-skills
/plugin install india-skills@india-skills
```

or from your shell: `claude plugin marketplace add akhilgarg07/india-skills && claude plugin install india-skills@india-skills`.
Skills load automatically when relevant. You can also invoke one directly, e.g. `/india-skills:gst-invoicing`.

To use them as plain (non-plugin) skills instead, copy folders into `~/.claude/skills/` (personal) or
`.claude/skills/` (project).

### OpenAI Codex

Codex reads skills from `.agents/skills/` in your repository (and parent folders up to the repo root) and
from `~/.agents/skills/` for your user:

```bash
git clone https://github.com/akhilgarg07/india-skills.git
mkdir -p ~/.agents/skills && cp -r india-skills/skills/* ~/.agents/skills/
# or, per project:  mkdir -p .agents/skills && cp -r india-skills/skills/gst-invoicing .agents/skills/
```

### Cursor

Cursor loads skills from `.agents/skills/` or `.cursor/skills/` in a project, and from `~/.agents/skills/` or
`~/.cursor/skills/` for your user (it also reads `.claude/skills/`):

```bash
mkdir -p .cursor/skills && cp -r india-skills/skills/upi-payments india-skills/skills/razorpay-integration .cursor/skills/
```

### Any other agent

These follow the open [Agent Skills](https://agentskills.io/specification) format (`SKILL.md` with
`name` + `description` frontmatter, plus `scripts/` and `references/`). Copy any folder from `skills/`
into your agent's skills directory. Each skill is self-contained.

## Using the scripts

All helpers are Python 3 standard library only, and each works as a CLI and an importable module:

```bash
python3 skills/indian-id-validation/scripts/gstin_validate.py 27AABCI2726B1CD
#  27AABCI2726B1CD  valid (Maharashtra, pan-based)
python3 skills/gst-tax-calculation/scripts/gst_calc.py 118000 --rate 18 --inclusive --inter-state
python3 skills/indian-number-formatting/scripts/amount_in_words.py 120000
#  One Lakh Twenty Thousand Rupees Only
python3 skills/tds-basics/scripts/tds_calc.py professional 60000 --no-pan --date 2026-05-10
python3 skills/upi-payments/scripts/upi_link.py build --pa merchant@okbank --pn "Asha Stores" --am 149.50 --tr ORD1001
```

## Before / after

Prompt: *"Generate a GST invoice for a ₹1,18,000 inter-state sale of software services from Karnataka
to Maharashtra. The buyer is a GST-registered company in Mumbai."*

| | Typical answer without the skill | With `gst-invoicing` |
|---|---|---|
| Tax type | CGST 9% + SGST 9% | **IGST 18%** (supplier state ≠ place of supply) |
| Tax amount | ₹21,240 (18% of ₹1,18,000) | Asks if ₹1,18,000 is inclusive. If so, **taxable ₹1,00,000 + IGST ₹18,000** |
| Code | HSN for "software" goods | **SAC 998314** (IT design & development services) |
| Mandatory fields | missing place of supply, reverse-charge flag | Place of supply **Maharashtra (27)**, "Reverse charge: No", ≤16-char invoice no. unique per FY |
| e-invoicing | not mentioned | IRN + signed QR required if turnover > ₹5 crore |

*The left column shows the failure patterns the eval graders check for; it is illustrative, not a recorded
run.* Measured results go in the table below.

### Eval results

`evals/` holds 36 realistic prompts (3-5 per skill), each with key-point graders, in the format of
[`claude plugin eval`](https://code.claude.com/docs/en/plugin-evals). It runs every case with and without
the plugin and reports the difference:

```bash
claude plugin eval . --no-publish            # all skills (runs 3x with plugin, 3x without)
claude plugin eval . --tag gst-invoicing     # one skill
```

| Skill | With plugin | Without | Δ |
|---|---|---|---|
| _run `claude plugin eval .` and paste the summary here_ | | | |

## Accuracy policy

- Every rate, threshold, format and API parameter is cited to an official source in
  `skills/<skill>/references/sources.md`, with a **last verified** date and how it was checked (full page
  read vs search extract).
- Unverified items are marked `TODO(verify)`. List them all with `python3 tools/check_skills.py --todos`
  (summary in [VERIFY.md](VERIFY.md)).
- Tax law moves: GST rates change with GST Council meetings, and TDS and income-tax rules change with each
  Union Budget. PRs that update a rule must update `sources.md`.

## Disclaimer

This repository is **not tax, legal or financial advice**. It is engineering guidance for developers,
summarising public official sources as of the dates shown. Rules change frequently, including with each
Union Budget and GST Council meeting. Always confirm current law and consult a qualified professional
before relying on it for compliance. Razorpay, NPCI, UPI and other names are trademarks of their owners;
this project is not affiliated with or endorsed by them.

## Contributing

Contributions are welcome: new skills, corrections, newer sources, more tests and evals. See
[CONTRIBUTING.md](CONTRIBUTING.md). In short: copy [`_template/`](_template), cite official sources in
`references/sources.md`, add pytest tests for every script, add 3-5 evals, and run
`pytest && python3 tools/check_skills.py` before opening a PR.

## License

[MIT](LICENSE)
