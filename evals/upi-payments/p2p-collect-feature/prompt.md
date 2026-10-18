---
description: Planning a P2P collect-request feature.
tags: [upi-payments, collect]
max_turns: 8
allowed_tools: [Read, Glob, Grep, Skill]
expected_outcome: >
  Flags that NPCI discontinued P2P collect requests from 1 Oct 2025; suggests
  alternatives (share a upi://pay link/QR for the friend to pay via intent); merchant
  collect differs.
---

We're a fintech app and want to add a 'request money from a friend' feature that sends a UPI collect request to the friend's VPA. How should we implement it?
