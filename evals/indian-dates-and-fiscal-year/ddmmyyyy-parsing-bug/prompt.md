---
description: Date parsing bug with DD/MM/YYYY input.
tags: [indian-dates-and-fiscal-year, parse]
max_turns: 8
allowed_tools: [Read, Glob, Grep, Skill]
expected_outcome: >
  new Date parses MM/DD (Jan 4); parse strictly with explicit format; validate; store
  ISO; display with Intl en-IN + day/month 2-digit, year numeric, timeZone Asia/Kolkata
  (dateStyle short gives 2-digit year).
---

Indian users type dates like 01/04/2026 into our React form and we do new Date(input). Some dates come out wrong. Fix it and show how to display dates back as DD/MM/YYYY in IST.
