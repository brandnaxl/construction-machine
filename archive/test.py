from enginge2 import calculate_aluminum, analyze_profitability

print("--- ANGKASA PROFIT SIMULATION ---")

# 1. INPUT: A batch of 4 windows
qty = 2
width = 135
height = 140
vendor_price =  2655820  # Per piece
brand = "astral_at"
glass = "clear_8mm"

print(f"Item: {brand} Window ({width}x{height}) - Qty: {qty}")

# 2. RUN ENGINE (Get Raw Numbers)
raw_data = calculate_aluminum(width, height, qty, vendor_price, glass, brand)

print(f"\nHarga Jual (Total): Rp {raw_data['selling']['total_price']:,.0f}")
print(f"Harga Modal (Total):  Rp {raw_data['costing']['total_cost']:,.0f}")


#add : harga Jual : alumunium , kaca , sealant 
# add : price after dics , net rev , ppn in , ppn out . 
print(f"\n")
print("Error Analysis (Harga Jual): ")
print(f"Harga Jual total : Rp {raw_data['selling']['total_price']:,.0f}")
print(f"Harga Jual kaca : Rp {raw_data['selling']['breakdown']['glass']:,.0f}")
print(f"Harga Jual aluminum :Rp {raw_data['selling']['breakdown']['alum']:,.0f}")
print(f"Harga Jual Sealant: Rp {raw_data['selling']['breakdown']['sealant']:,.0f}")

# cek harga, modal satuan 
print(f"\n")
print("Error Analysis (Harga Modal satuan): ")
print(f"Harga modal total : Rp {raw_data['costing']['total_cost']:,.0f}")
print(f"Harga modal kaca : Rp {raw_data['costing']['kaca_base_cost']:,.0f}")
print(f"Harga modal aluminum :Rp {raw_data['costing']['vendor_base_total']:,.0f}")
print(f"Harga modal sealant :Rp {raw_data['costing']['sealant_base_cost']:,.0f}")
print(f"Harga modal tenaga : Rp {raw_data['costing']['manpower_base_cost']:,.0f}")
print(f"\n")

# 3. NEGOTIATION SCENARIO
# Let's say we give a "Contractor Price" (20% Disc) + 3% Fee
my_discount = 35 # %
arch_fee = 5    # %

print(f"\n--- APPLYING SCENARIO: Disc {my_discount}% | Fee {arch_fee}% ---")
profit_analysis = analyze_profitability(raw_data, my_discount, arch_fee)

print(f"\n--- RINGKASAN FINANSIAL (Setelah Disc {my_discount}%) ---")
# 1. Harga Sebelum Pajak (Net Sales)

print(f"Net Revenue (After Disc/Fee): Rp {profit_analysis['final_price']:,.0f}")
print(f"PPN OUT :                     Rp {profit_analysis['debug']['ppn_out']:,.0f}")
print(f"PPN IN  :                     Rp: {profit_analysis['debug']['ppn_in']:,.0f}")
print(f"PPN Difference (To Pay):      Rp {profit_analysis['debug']['ppn_diff']:,.0f}")
print(f"Real Cost (COGS):             Rp {profit_analysis['total_base_cost']:,.0f}")
print("-" * 40)
print(f"GROSS INCOME (PROFIT):        Rp {profit_analysis['gross_income']:,.0f}")
print(f"MARGIN:                       {profit_analysis['margin_percent']}%")

if profit_analysis['margin_percent'] < 15:
    print("\n[ALERT] Margin is too low! Review discount.")
else:
    print("\n[OK] Profit is healthy.")