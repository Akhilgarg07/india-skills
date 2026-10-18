# GST rounding: rules and edge cases

## What the law says

Section 170 CGST Act ("Rounding off of tax, etc."): the amount of tax, interest, penalty,
fine or any other sum payable, and refunds or any other sum due, under the Act "shall be
rounded off to the nearest rupee and, for this purpose, where such amount contains a part
of a rupee consisting of paise, then, if such part is fifty paise or more, it shall be
increased to one rupee and if such part is less than fifty paise it shall be ignored."

That is half-up rounding to whole rupees, applied to amounts payable or refundable under the
Act. The CGST Rules do not prescribe a paise-level rounding method for each invoice line.

## Recommended implementation

1. Store money as integer paise or a decimal type. Never float.
   - Python `decimal.Decimal`, Java `BigDecimal`, JS `decimal.js`/`big.js` or integer paise,
     PostgreSQL `numeric(14,2)`.
2. Per line: `taxable = qty × unit_price − line_discount` (rounded to paise).
3. Per line, per component: `cgst = round_half_up(taxable × cgst_rate / 100, 2)`; same for
   SGST. IGST likewise. Because CGST and SGST rates are equal, the amounts are equal.
4. Invoice totals = sums of line values. Don't recompute tax on the invoice total; the
   per-line sum can differ by a few paise, and the per-line figure is the one shown per line.
5. Optional: round the grand total to the nearest rupee and print the difference as
   "Round off" (it can be negative). Keep tax amounts unchanged.

## Inclusive (MRP) prices

```
tax_exact = P × r / (100 + r)
cgst = sgst = round_half_up(tax_exact / 2, 2)      # intra-state
igst = round_half_up(tax_exact, 2)                 # inter-state
taxable = P − cgst − sgst − igst                   # guarantees taxable + tax == P
```

Example: P = ₹101, 18% intra-state: tax_exact = 15.4068; CGST = SGST = 7.70;
taxable = 85.60; 85.60 + 7.70 + 7.70 = 101.00.

## Common bugs

- `0.1 + 0.2` float errors producing ₹0.30000000000000004 of tax.
- Python's `round()` is banker's rounding (`round(2.675, 2) == 2.67` because of float and
  half-even). Use `Decimal.quantize(..., ROUND_HALF_UP)`.
- JavaScript `toFixed` on floats has similar issues (`(1.005).toFixed(2) === "1.00"`).
- Splitting `total_tax` as `cgst = round(total/2)` and `sgst = total − cgst` gives
  unequal halves (₹7.71 / ₹7.70). Compute each half from the taxable value.
- Rounding the tax up "to be safe". Overcharging GST is not safe; it is collecting tax not due.
