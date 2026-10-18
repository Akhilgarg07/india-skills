---
description: Mobile number validation that rejects common Indian input formats.
tags: [indian-id-validation, mobile]
max_turns: 8
allowed_tools: [Read, Glob, Grep, Skill]
expected_outcome: >
  Strips separators, accepts +91 / 91 / 0 prefixes, requires 10 digits starting 6-9,
  stores E.164 (+91XXXXXXXXXX), and notes that ownership needs OTP.
---

Our Python signup validation is `re.fullmatch(r"[0-9]{10}", phone)`. Users complain that "+91 98765-43210" and "09876543210" are rejected, while "1234567890" is accepted. Fix it and tell me how we should store the numbers.
