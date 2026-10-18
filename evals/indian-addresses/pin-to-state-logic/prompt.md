---
description: Deriving state from PIN code.
tags: [indian-addresses, pin]
max_turns: 8
allowed_tools: [Read, Glob, Grep, Skill]
expected_outcome: >
  No: first two digits are postal circles, not states (e.g. Telangana inside 50-53
  range, Chandigarh 160 inside Punjab range); use All India Pincode Directory; warn
  instead of reject.
---

Can I derive the customer's state from the first two digits of their PIN code with a lookup table, and reject the form if they pick a different state?
