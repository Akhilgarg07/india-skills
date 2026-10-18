# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses
[Semantic Versioning](https://semver.org/).

## [0.1.0] - 2026-10-18

First release. All facts last verified on 2026-10-18 (see each skill's `references/sources.md`).

### Added
- **Skills (10):** `gst-invoicing`, `gst-tax-calculation`, `tds-basics`, `indian-id-validation`,
  `upi-payments`, `razorpay-integration`, `indian-number-formatting`, `indian-addresses`,
  `dpdp-privacy`, `indian-dates-and-fiscal-year`.
- **Scripts (stdlib Python, CLI + module):** `gstin_validate.py`, `pan_validate.py`, `ifsc_validate.py`,
  `mobile_validate.py`, `pincode_validate.py`, `verhoeff.py`, `aadhaar_validate.py`, `gst_calc.py`,
  `invoice_check.py`, `tds_calc.py`, `upi_link.py`, `razorpay_signature.py`, `inr_format.py`,
  `amount_in_words.py`, `india_regions.py`, `fiscal_year.py`.
- **Tests:** pytest suite for every script (413 tests), including real published GSTINs, RFC 4231
  HMAC vectors, and cross-checks against Node's `Intl.NumberFormat`.
- **Evals:** 36 `claude plugin eval` cases with key-point graders and skill-fired checks.
- **Packaging:** Claude Code plugin manifest and single-plugin marketplace (`.claude-plugin/`).
- **Tooling:** `tools/check_skills.py` (Agent Skills spec + repo-rule linter, `--todos`), GitHub Actions CI,
  `_template/` for new skills, `CONTRIBUTING.md`, `VERIFY.md`.

### Coverage notes
- GST rates reflect the 56th GST Council rationalisation (22 Sep 2025) and the 1 Feb 2026 tobacco/pan
  masala changes. The 57th GST Council (8 Oct 2026) recommendations are noted where relevant.
- TDS reflects the Income-tax Act, 2025 (in force 1 Apr 2026) section mapping alongside the 1961 Act.
- DPDP reflects the DPDP Rules, 2025 (Gazette of 13 Nov 2025) and their phased commencement.
