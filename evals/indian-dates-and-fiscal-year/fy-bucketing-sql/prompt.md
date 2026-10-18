---
description: Grouping revenue by Indian financial year from UTC timestamps.
tags: [indian-dates-and-fiscal-year, fy, ist]
max_turns: 8
allowed_tools: [Read, Glob, Grep, Skill]
expected_outcome: >
  Convert to Asia/Kolkata before bucketing; FY starts 1 April (month >= 4 → year else
  year-1); label like 2026-27; quarters Q1 Apr-Jun ... Q4 Jan-Mar.
---

Our Postgres payments table has created_at timestamptz stored in UTC. Write a query for revenue by Indian financial year and quarter. Finance says a payment at 11:30 pm UTC on 31 March belongs to the next year.
