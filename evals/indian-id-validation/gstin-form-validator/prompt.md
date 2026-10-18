---
description: GSTIN validation in a vendor onboarding form, starting from a common but wrong regex.
tags: [indian-id-validation, gstin]
max_turns: 10
allowed_tools: [Read, Glob, Grep, Skill]
expected_outcome: >
  A TypeScript validator that normalises input, checks the GST state code, verifies the
  mod-36 check character, does not hard-code 'Z' as the 14th character, and explains that
  a valid format does not prove the GSTIN is registered.
---

Our vendor onboarding form validates GSTIN with this regex:

/^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][1-9A-Z]Z[0-9A-Z]$/

A vendor says their GSTIN 27AABCI2726B1CD is being rejected, and we also let through obvious typos. Write a proper TypeScript `validateGstin()` for the form and tell me what was wrong with the regex.
