import streamlit as st
import pandas as pd
from enginge2 import calculate_aluminum, analyze_profitability
from decimal import Decimal

st.set_page_config(page_title="Angkasa Estimator", page_icon="🏗️", layout="wide")

st.title("🏗️ Angkasa Bangunan - Project Estimator")
st.markdown("Sistem Kalkulasi Penawaran Multi-Item")
st.markdown("---")

# ==========================================
# INISIALISASI MEMORI (SESSION STATE)
# ==========================================
if "keranjang_proyek" not in st.session_state:
    st.session_state["keranjang_proyek"] = []

# Bikin "Lampu Sein" untuk mendeteksi apakah kita lagi mode nambah atau mode ngedit
if "edit_index" not in st.session_state:
    st.session_state["edit_index"] = None 

# ==========================================
# BAGIAN 1: FORM INPUT / EDIT ITEM
# ==========================================
is_edit_mode = st.session_state["edit_index"] is not None
edit_idx = st.session_state["edit_index"]

# 1. Siapkan Nilai Default (Kosong/Standar)
def_name = "J1"
def_brand_idx = 1 # astral_at
def_glass_idx = 1 # clear_8mm
def_qty = 1
def_w = 145
def_h = 185
def_vendor_tot = 2429100

# 2. Kalau Lampu Sein Edit Nyala, Ganti Nilai Default pakai data lama
if is_edit_mode:
    item_lama = st.session_state["keranjang_proyek"][edit_idx]
    def_name = item_lama["meta"]["nama_item"]
    
    # Mapping nama ke urutan list (Biar dropdownnya pas)
    brand_list = ["astral_ap", "astral_at", "astral_as", "astral_lm", "ykk_nexta"]
    glass_list = ["clear_6mm", "clear_8mm", "clear_10mm", "tempered_8mm", "insulated_5+A10+5mm"]
    old_brand = item_lama["meta"].get("brand_name", item_lama["meta"].get("brand_used", "astral_at"))
    old_glass = item_lama["meta"].get("glass_type", item_lama["meta"].get("glass_used", "clear_8mm"))
    
    def_brand_idx = brand_list.index(old_brand) if old_brand in brand_list else 1
    def_glass_idx = glass_list.index(old_glass) if old_glass in glass_list else 1
    
    def_qty = int(item_lama["meta"]["quantity"])
    def_w = int(item_lama["meta"]["width_cm"])
    def_h = int(item_lama["meta"]["height_cm"])
    
    # Vendor total lama = harga modal satuan x qty
    def_vendor_tot = int(item_lama["meta"]["vendor_base_price"] * def_qty)

# 3. Tampilkan UI Formnya
if is_edit_mode:
    st.header(f"✏️ Edit Item: {def_name} (Baris ke-{edit_idx + 1})")
else:
    st.header("1. Tambah Item Jendela/Pintu")

with st.container(border=True):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        nama_item = st.text_input("Nama Item (Contoh: J1, PJ1)", value=def_name)
        brand = st.selectbox("Brand Aluminum", ["astral_ap", "astral_at", "astral_as", "astral_lm", "ykk_nexta"], index=def_brand_idx)
        glass = st.selectbox("Jenis Kaca", ["clear_6mm", "clear_8mm", "clear_10mm", "tempered_8mm", "insulated_5+A10+5mm"], index=def_glass_idx)
        
    with col2:
        qty = st.number_input("Quantity (Jumlah Lubang)", min_value=1, value=def_qty)
        width = st.number_input("Lebar Jendela (cm)", min_value=10, value=def_w)
        height = st.number_input("Tinggi Jendela (cm)", min_value=10, value=def_h)
        
    with col3:
        # input harga vendor total, bukan satuan
        vendor_price_total = st.number_input("Harga Modal Vendor (TOTAL KESELURUHAN)", min_value=0, value=def_vendor_tot, step=100000)
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Atur tombol simpan / tambah
        btn_label = "💾 Simpan Perubahan" if is_edit_mode else "➕ Tambah ke Proyek"
        btn_type = "primary" if is_edit_mode else "secondary"
        
        col_btn1, col_btn2 = st.columns([3, 1]) # Buat tombol batal jika lagi ngedit
        with col_btn1:
            if st.button(btn_label, type=btn_type, use_container_width=True):
                # LOGIKA PEMBAGIAN HARGA VENDOR (Front-end yang lakuin)
                vendor_price_satuan = vendor_price_total / qty if qty > 0 else 0
                #ubah ke decimal
                vendor_price_satuan = Decimal(str(vendor_price_satuan))
                
                # Panggil mesin dengan harga satuan
                hasil_item = calculate_aluminum(width, height, qty, vendor_price_satuan, glass, brand)
                hasil_item["meta"]["nama_item"] = nama_item
                
                if is_edit_mode:
                    # REPLACE (TIMPA) DATA LAMA
                    st.session_state["keranjang_proyek"][edit_idx] = hasil_item
                    st.session_state["edit_index"] = None # Matikan lampu sein
                    st.success(f"Berhasil mengubah {nama_item}!")
                else:
                    # TAMBAH BARANG BARU
                    st.session_state["keranjang_proyek"].append(hasil_item)
                    st.success(f"{nama_item} berhasil ditambahkan!")
                st.rerun() # Refresh web
                
        with col_btn2:
            if is_edit_mode:
                if st.button("❌ Batal"):
                    st.session_state["edit_index"] = None
                    st.rerun()

# ==========================================
# BAGIAN 2: TABEL KERANJANG (CUSTOM COLUMNS)
# ==========================================
st.header(f"2. Rincian Proyek ({len(st.session_state['keranjang_proyek'])} Item)")

if len(st.session_state["keranjang_proyek"]) > 0:
    # Buat header tabel manual biar bisa taruh tombol di ujung
    t_col1, t_col2, t_col3, t_col4, t_col5, t_col6, t_col7, t_col8, t_col9, t_col10 = st.columns([1, 2, 1, 2, 2, 1.5, 1.5, 2, 2.5, 1.5])
    t_col1.write("**No**")
    t_col2.write("**Item**")
    t_col3.write("**Qty**")
    t_col4.write("**Brand**")
    t_col5.write("**Kaca**")
    t_col6.write("**L (cm)**")
    t_col7.write("**T (cm)**")
    t_col8.write("**Hrg Satuan**")
    t_col9.write("**Hrg Total**")
    t_col10.write("**Aksi**")
    st.divider()
    
    # Nge-print isi keranjang baris per baris
    for i, item in enumerate(st.session_state["keranjang_proyek"]):
        c1, c2, c3, c4, c5, c6, c7, c8, c9, c10 = st.columns([1, 2, 1, 2, 2, 1.5, 1.5, 2, 2.5, 1.5])
        c1.write(i + 1)
        c2.write(item["meta"]["nama_item"])
        c3.write(item["meta"]["quantity"])
        c4.write(item["meta"]["brand_used"].replace("astral_", "").upper())
        #c5.write(str(glass_used).replace("_", " ").upper())
        c5.write(item["meta"]["glass_used"].replace("_"," ").upper())
        c6.write(item["meta"]["width_m"])
        c7.write(item["meta"]["height_m"])
        c8.write(f"Rp {item['selling']['unit_price']:,.0f}")
        c9.write(f"Rp {item['selling']['total_price']:,.0f}")
        
        with c10:
            # Jejerin tombol Edit & Delete
            act1, act2 = st.columns(2)
            if act1.button("✏️", key=f"edit_{i}"):
                st.session_state["edit_index"] = i # Nyalakan lampu sein edit
                st.rerun()
            if act2.button("🗑️", key=f"del_{i}"):
                st.session_state["keranjang_proyek"].pop(i) # Buang dari list
                if st.session_state["edit_index"] == i:
                    st.session_state["edit_index"] = None
                st.rerun()

    if st.button("🗑️ Kosongkan Seluruh Keranjang", type="secondary"):
        st.session_state["keranjang_proyek"] = []
        st.session_state["edit_index"] = None
        st.rerun()
else:
    st.info("Keranjang proyek masih kosong. Silakan tambah item di atas.")

st.markdown("---")

# ==========================================
# BAGIAN 3: NEGOSIASI & TOTAL
# ==========================================
st.header("3. Negosiasi & Profitabilitas Proyek")
col4, col5 = st.columns(2)

with col4:
    my_discount = st.slider("Diskon Proyek ke Client (%)", min_value=0, max_value=50, value=35)
with col5:
    arch_fee = st.slider("Fee Arsitek/Kontraktor (%)", min_value=0, max_value=20, value=0)

if len(st.session_state["keranjang_proyek"]) > 0:
    if st.button("Hitung Profit Total 🚀", type="primary", use_container_width=True):
        profit_analysis = analyze_profitability(st.session_state["keranjang_proyek"], my_discount, arch_fee)
        st.success("Kalkulasi Total Proyek Selesai!")
        
        m1, m2, m3 = st.columns(3)
        m1.metric(label="Grand Total Deal Klien (+PPN)", value=f"Rp {profit_analysis['final_price']:,.0f}")
        m2.metric(label="Total Modal Proyek (COGS)", value=f"Rp {profit_analysis['total_base_cost']:,.0f}")
        m3.metric(label="Profit Bersih Proyek", 
                  value=f"Rp {profit_analysis['gross_income']:,.0f}", 
                  delta=f"{profit_analysis['margin_percent']}% Margin",
                  delta_color="normal" if profit_analysis['margin_percent'] >= 15 else "inverse")
        
        # Rincian Modal
        st.divider()
        st.write("**📦 Rincian Total Modal Proyek (Material & Tenaga):**")
        tot_alum = sum(item["costing"]["vendor_base_total"] for item in st.session_state["keranjang_proyek"])
        tot_kaca = sum(item["costing"].get("kaca_base_cost", 0) for item in st.session_state["keranjang_proyek"])
        tot_sealant = sum(item["costing"].get("sealant_base_cost", 0) for item in st.session_state["keranjang_proyek"])
        tot_tenaga = sum(item["costing"].get("manpower_base_cost", 0) for item in st.session_state["keranjang_proyek"])

        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        col_m1.metric("Modal Alumunium", f"Rp {tot_alum:,.0f}")
        col_m2.metric("Modal Kaca", f"Rp {tot_kaca:,.0f}")
        col_m3.metric("Modal Sealant", f"Rp {tot_sealant:,.0f}")
        col_m4.metric("Tenaga Tukang", f"Rp {tot_tenaga:,.0f}")

        st.divider()
        st.write("**Detail Transparansi Pajak & Diskon:**")
        st.write(f"- Total RAB Awal (Kasar): Rp {profit_analysis['grand_list_price']:,.0f}")
        st.write(f"- Total Diskon ({my_discount}%): Rp {profit_analysis['debug']['discount_amount']:,.0f}")
        st.write(f"- Selisih PPN Disetor: Rp {profit_analysis['debug']['ppn_diff']:,.0f}")




# ==========================================
        # BAGIAN 4: DATA KLIEN & CETAK PDF
        # ==========================================
        st.markdown("---")
        st.header("4. Data Klien & Cetak Penawaran")
        
        with st.container(border=True):
            c_klien1, c_klien2 = st.columns(2)
            with c_klien1:
                nama_klien = st.text_input("Nama Customer", placeholder="Cth: Bp. Hengky")
                lokasi_klien = st.text_input("Lokasi Proyek", placeholder="Cth: Jakarta")
            with c_klien2:
                default_note = """- Harga sudah termasuk instalasi diluar pekerjaan sipil (bobok dan plester)
- Garansi warna 10 tahun dan hardware 1 tahun
- Waktu produksi pabrikasi 40 - 65 hari kerja dari ACC Shopdrawing
- DP 50% diawal pengerjaan
- Penawaran ini berlaku 14 hari."""
                note_tambahan = st.text_area("Note / Syarat & Ketentuan", value=default_note, height=150)
        
        # Siapkan data untuk dikirim ke pdf_maker.py
        client_data = {
            "nama": nama_klien if nama_klien else "Customer",
            "lokasi": lokasi_klien if lokasi_klien else "-",
            "note": note_tambahan,
            "diskon_persen": my_discount
        }
        
        # Panggil fungsi dari file sebelah
        from pdf_maker import generate_quotation_pdf
        
        pdf_file = generate_quotation_pdf(st.session_state["keranjang_proyek"], profit_analysis, client_data)
        
        st.download_button(
            label="📄 DOWNLOAD INVOICE PENAWARAN (PDF)",
            data=pdf_file,
            file_name=f"Penawaran_Angkasa_{nama_klien}.pdf",
            mime="application/pdf",
            type="primary",
            use_container_width=True
        )