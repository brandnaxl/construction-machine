# Parity Result — cm→mm migration verified

## Task 5: Parity Test

Re-entered the three baseline items in **millimeters** (same physical sizes):
- 1000 × 1000 mm (was 100 × 100 cm)
- 1500 × 800 mm (was 150 × 80 cm)
- 2000 × 1200 mm (was 200 × 120 cm)

Same conditions: ABJ (Angkasa Bangunan Jakarta, PPN=True), 0% discount, 0% arch fee, vendor Rp 1.000.000 total/item.

### Item-level results

| Item | Field | Baseline (cm) | mm result | Match |
|------|-------|--------------|-----------|-------|
| 1000×1000 | unit_price | Rp 3.618.000 | Rp 3.618.000 | ✓ |
| 1000×1000 | total_price | Rp 3.618.000 | Rp 3.618.000 | ✓ |
| 1000×1000 | alum breakdown | Rp 2.620.000 | Rp 2.620.000 | ✓ |
| 1000×1000 | glass breakdown | Rp 518.000 | Rp 518.000 | ✓ |
| 1000×1000 | sealant breakdown | Rp 480.000 | Rp 480.000 | ✓ |
| 1000×1000 | unit_cost | Rp 1.866.000 | Rp 1.866.000 | ✓ |
| 1000×1000 | total_cost | Rp 1.866.000 | Rp 1.866.000 | ✓ |
| 1500×800 | unit_price | Rp 2.648.600 | Rp 2.648.600 | ✓ |
| 1500×800 | total_price | Rp 5.297.200 | Rp 5.297.200 | ✓ |
| 1500×800 | alum breakdown | Rp 2.950.000 | Rp 2.950.000 | ✓ |
| 1500×800 | glass breakdown | Rp 1.243.200 | Rp 1.243.200 | ✓ |
| 1500×800 | sealant breakdown | Rp 1.104.000 | Rp 1.104.000 | ✓ |
| 1500×800 | unit_cost | Rp 1.527.200 | Rp 1.527.200 | ✓ |
| 1500×800 | total_cost | Rp 3.054.400 | Rp 3.054.400 | ✓ |
| 2000×1200 | unit_price | Rp 4.631.200 | Rp 4.631.200 | ✓ |
| 2000×1200 | total_price | Rp 4.631.200 | Rp 4.631.200 | ✓ |
| 2000×1200 | alum breakdown | Rp 2.620.000 | Rp 2.620.000 | ✓ |
| 2000×1200 | glass breakdown | Rp 1.243.200 | Rp 1.243.200 | ✓ |
| 2000×1200 | sealant breakdown | Rp 768.000 | Rp 768.000 | ✓ |
| 2000×1200 | unit_cost | Rp 2.886.400 | Rp 2.886.400 | ✓ |
| 2000×1200 | total_cost | Rp 2.886.400 | Rp 2.886.400 | ✓ |

### Grand totals

| Metric | Baseline | mm result | Match |
|--------|----------|-----------|-------|
| grand_list_price | Rp 13.548.000 | Rp 13.548.000 | ✓ |
| final_price | Rp 13.548.000 | Rp 13.548.000 | ✓ |
| total_base_cost | Rp 7.807.000 | Rp 7.807.000 | ✓ |
| gross_income | Rp 4.696.000 | Rp 4.696.000 | ✓ |
| margin_percent | 34.7% | 34.7% | ✓ |

**VERDICT: ALL PASS — outputs are identical to the rupiah. Merge gate cleared.**

---

## Task 6: Second Independent Recheck

Re-read every changed conversion line in isolation to verify correctness and absence of stale references:

**enginge2.py lines 18–21 (after migration):**
```python
area_m2 = Decimal(width_mm) * Decimal(height_mm) / Decimal('1000000')
area_m  = Decimal('4') * (Decimal(width_mm) + Decimal(height_mm)) / Decimal('1000')
width_m = Decimal(width_mm) / Decimal('1000')
height_m = Decimal(height_mm) / Decimal('1000')
```

Verification confirms: `area_m2` divides by `1000000` (mm² → m²); `area_m` divides by `1000` (mm → m) preserving the original `4*(w+h)` coefficient; both `width_m` and `height_m` are derived correctly with `/1000`. A `grep` for `width_cm`, `height_cm`, `/100`, `10000` in the active code path (`enginge2.py`, `app.py`, `pdf_maker.py`, `xlsx_maker.py`) returns zero hits — no stale cm references remain. The glass price (per m²), sealant rate (per m), manpower rate (per m²), aluminum multiplier, PPN rate, architect fee, discount logic, and `ceiling_1000` rounding in `analyze_profitability` are untouched; their values are read unchanged from `pricing.json` and the UI sliders.
