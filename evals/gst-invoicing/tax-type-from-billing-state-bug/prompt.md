---
description: Bug where tax type is chosen from billing address instead of place of supply for goods.
tags: [gst-invoicing, place-of-supply]
max_turns: 8
allowed_tools: [Read, Glob, Grep, Skill]
expected_outcome: >
  For goods with movement, the place of supply is where delivery terminates (Rajasthan),
  so it is inter-state and IGST applies. For unregistered buyers, record the delivery
  address on the invoice. Use place of supply, not billing state.
---

Our e-commerce site (seller registered in Gujarat) decides IGST vs CGST+SGST by comparing our state with the customer's *billing* address state. A customer billed in Gujarat had the order shipped to Rajasthan. We charged CGST+SGST. Is that correct? How should the logic work?
