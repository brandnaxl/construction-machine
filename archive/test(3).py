from enginge2 import calculate_aluminum, analyze_profitability

print("=== 🏗️ ANGKASA PROJECT SIMULATION ===")

# 1. KITA BUAT KERANJANG PROYEK KOSONG
keranjang_proyek = []

# 2. MASUKKAN ITEM 1: Jendela Utama (2 Lubang)
print("\n[+] Menghitung Jendela Utama (2 Qty)...")
J1 = calculate_aluminum(width_cm=145, height_cm=185, quantity=2, 
                                   vendor_base_price=2429100, glass_type="clear_10mm", brand_name="astral_ap")
keranjang_proyek.append(J1) # Masukkan ke keranjang

# 3. MASUKKAN ITEM 2: Jendela Toilet (1 Lubang)
print("[+] Menghitung Jendela Toilet (1 Qty)...")
PJ1 = calculate_aluminum(width_cm=220, height_cm=247, quantity=1, 
                                    vendor_base_price=12370300, glass_type="clear_8mm", brand_name="astral_ap")
keranjang_proyek.append(PJ1) # Masukkan ke keranjang


# 4. NEGOSIASI GLOBAL (UNTUK TOTAL PROYEK)
my_discount = 35 
arch_fee = 0     

print(f"\n=== MENGHITUNG TOTAL PROYEK ({len(keranjang_proyek)} JENIS BARANG) ===")
# Mesin memproses SELURUH isi keranjang sekaligus
profit_analysis = analyze_profitability(keranjang_proyek, my_discount, arch_fee)

print(f"Grand Total RAB (List Price) : Rp {profit_analysis['grand_list_price']:,.0f}")
print(f"Diskon Proyek ({my_discount}%)           : Rp {profit_analysis['debug']['discount_amount']:,.0f}")
print(f"HARGA DEAL KLIEN (Net/Inclus): Rp {profit_analysis['final_price']:,.0f}")  # INI YG DITRANSFER KLIEN
print("-" * 45)
print(f"Total Modal Proyek (COGS)    : Rp {profit_analysis['total_base_cost']:,.0f}")
print(f"Selisih PPN Disetor          : Rp {profit_analysis['debug']['ppn_diff']:,.0f}")
print(f"Fee Arsitek ({arch_fee}%)               : Rp {profit_analysis['debug']['architect_fee']:,.0f}")
print("-" * 45)
print(f"PROFIT BERSIH PROYEK         : Rp {profit_analysis['gross_income']:,.0f}")
print(f"MARGIN PROYEK                : {profit_analysis['margin_percent']}%")

if profit_analysis['margin_percent'] < 15:
    print("\n[⚠️ ALERT] Margin Proyek Terlalu Rendah!")
else:
    print("\n[✅ OK] Margin Proyek Sehat.")


    
    
