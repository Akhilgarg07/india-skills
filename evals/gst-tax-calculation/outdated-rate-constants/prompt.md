---
description: Code still using the pre-September-2025 slabs.
tags: [gst-tax-calculation, rates]
max_turns: 8
allowed_tools: [Read, Glob, Grep, Skill]
expected_outcome: >
  Points out the 22 Sep 2025 rate rationalisation (5/18/40 plus special rates), that 12%
  and 28% are gone for almost all goods, and that rates should be keyed by HSN/SAC and
  effective date.
---

Review this Python constant used by our billing service in October 2026: `GST_SLABS = {"low": 5, "mid": 12, "high": 18, "luxury": 28}`. We assign a slab per product category. Anything wrong?
