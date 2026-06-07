# Parity Baseline — cm inputs (BEFORE migration)

Captured **before** any cm→mm code change.
Engine: `enginge2.py` at commit on branch `main`.
Company: **Angkasa Bangunan Jakarta** (ABJ, kena_ppn=True).
Discount: **0%**. Architect fee: **0%**.
Vendor default: Rp 1.000.000 total per item.

---

## Conversion logic found in enginge2.py (Task 1 inventory)

```
width_m  = Decimal(width_cm) / Decimal(100)          # /100
height_m = Decimal(height_cm) / Decimal(100)          # /100
area_m2  = width_m * height_m                         # ≡ w_cm*h_cm / 10000
area_m   = (Decimal('4')*width_m)+(Decimal('4')*height_m)  # 4*(w+h) in m — NOT standard 2*(w+h)
```

All references to rename (cm → mm):
| File | Line | Reference |
|------|------|-----------|
| enginge2.py | 17 | function param `width_cm, height_cm` |
| enginge2.py | 18 | `Decimal(width_cm) / Decimal(100)` |
| enginge2.py | 19 | `Decimal(height_cm) / Decimal(100)` |
| enginge2.py | 88 | `"width_cm": width_cm` in return meta |
| enginge2.py | 89 | `"height_cm": height_cm` in return meta |
| app.py | 82-83 | `def_w = 100`, `def_h = 100` (default cm values) |
| app.py | 107 | `item_lama["meta"]["width_cm"]` |
| app.py | 108 | `item_lama["meta"]["height_cm"]` |
| app.py | 135 | label `"Lebar Jendela (cm)"`, `min_value=10` |
| app.py | 136 | label `"Tinggi Jendela (cm)"`, `min_value=10` |
| app.py | 170 | `calculate_aluminum(width, height, ...)` (var names) |
| app.py | 234 | `item['meta']['width_cm']`, `item['meta']['height_cm']` in spek_custom |

---

## Baseline item outputs

### Item 1: 100 × 100 cm, Astral AT, Clear 6mm, qty 1

| Field | Value |
|-------|-------|
| area_m2 | 1.0 |
| width_m | 1 |
| height_m | 1 |
| Selling unit_price | Rp 3.618.000 |
| Selling total_price | Rp 3.618.000 |
| Breakdown: alum | Rp 2.620.000 |
| Breakdown: glass | Rp 518.000 |
| Breakdown: sealant | Rp 480.000 |
| COGS unit_cost | Rp 1.866.000 |
| COGS total_cost | Rp 1.866.000 |

### Item 2: 150 × 80 cm, Astral AS, Clear 6mm, qty 2

| Field | Value |
|-------|-------|
| area_m2 | 1.2 |
| width_m | 1.5 |
| height_m | 0.8 |
| Selling unit_price | Rp 2.648.600 |
| Selling total_price | Rp 5.297.200 |
| Breakdown: alum (total) | Rp 2.950.000 |
| Breakdown: glass (total) | Rp 1.243.200 |
| Breakdown: sealant (total) | Rp 1.104.000 |
| COGS unit_cost | Rp 1.527.200 |
| COGS total_cost | Rp 3.054.400 |

### Item 3: 200 × 120 cm, Astral LM, Clear 6mm, qty 1

| Field | Value |
|-------|-------|
| area_m2 | 2.4 |
| width_m | 2 |
| height_m | 1.2 |
| Selling unit_price | Rp 4.631.200 |
| Selling total_price | Rp 4.631.200 |
| Breakdown: alum | Rp 2.620.000 |
| Breakdown: glass | Rp 1.243.200 |
| Breakdown: sealant | Rp 768.000 |
| COGS unit_cost | Rp 2.886.400 |
| COGS total_cost | Rp 2.886.400 |

---

## Grand Totals (all 3 items, ABJ, 0% discount)

| Metric | Value |
|--------|-------|
| grand_list_price | Rp 13.548.000 |
| final_price | Rp 13.548.000 |
| total_base_cost | Rp 7.807.000 |
| gross_income | Rp 4.696.000 |
| margin_percent | 34.7% |
| debug.discount_amount | Rp 0 |
| debug.architect_fee | Rp 0 |
| debug.ppn_diff | 1045297.297297... |
| debug.ppn_in | 297297.297297... |
| debug.ppn_out | 1342594.594594... |
