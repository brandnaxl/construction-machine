import streamlit as st
import pandas as pd
from enginge2 import calculate_aluminum, analyze_profitability # (Gua benerin typo 'enginge2' lu ya)
from decimal import Decimal
import streamlit.components.v1 as components
import time

st.set_page_config(page_title="Angkasa Estimator", page_icon="🏗️", layout="wide")

st.title("🏗️ Angkasa Bangunan - Project Estimator")
st.markdown("Sistem Kalkulasi Penawaran Multi-Item")
st.markdown("---")
# 🟢 FITUR AUTO-SCROLL KE ATAS 
if st.session_state.get("scroll_up", False):
    # Kita bikin scriptnya selalu 'baru' di mata Streamlit dengan nambahin waktu (time.time)
    # Kita hajar semua kemungkinan container scroll yang ada di Streamlit
    js_scroll = f"""
    <script id="scroll-hack-{time.time()}">
        // Fungsi untuk nyari siapa sebenarnya bos yang megang scrollbar
        const targets = [
            window.parent.document.querySelector('[data-testid="stAppViewContainer"]'),
            window.parent.document.querySelector('.main'),
            window.parent.document.documentElement,
            window.parent.window
        ];
        
        // Tembak semuanya satu-satu sampai ada yang mau naik
        for (let target of targets) {{
            if (target) {{
                try {{
                    target.scrollTo({{top: 0, behavior: 'smooth'}});
                }} catch(e) {{}}
            }}
        }}
    </script>
    """
    components.html(js_scroll, height=0)
    
    # Matiin lampu sein
    st.session_state["scroll_up"] = False
# FITUR TAMBAHAN: LIHAT DATABASE HARGA
with st.expander("👀 Cek Database Harga Dasar & Material"):
    import json
    try:
        # Buka dan baca file pricing.json lu
        with open("pricing.json", "r") as f:
            data_harga = json.load(f)
            
        # Tampilkan dalam bentuk struktur JSON yang rapi
        st.json(data_harga)
        
        # Opsi Tambahan: Kalau lu mau nampilin text penjelasan buat estimator
        st.info("💡 Note: Data di atas adalah harga modal dasar (COGS) dari vendor sebelum dikalikan markup/multiplier.")
        
    except FileNotFoundError:
        st.error("⚠️ File pricing.json tidak ditemukan di dalam folder. Pastikan namanya sudah benar.")
# INISIALISASI MEMORI (SESSION STATE)
if "keranjang_proyek" not in st.session_state:
    st.session_state["keranjang_proyek"] = []
# Bikin "Lampu Sein" untuk mendeteksi lagi mode nambah atau mode ngedit
if "edit_index" not in st.session_state:
    st.session_state["edit_index"] = None 
# Memori buat n-trigger scroll ke atas
if "scroll_up" not in st.session_state:
    st.session_state["scroll_up"] = False





# ==========================================
# BAGIAN 1: FORM INPUT / EDIT ITEM
# ==========================================
is_edit_mode = st.session_state["edit_index"] is not None
edit_idx = st.session_state["edit_index"]

# 1. Siapkan Nilai Default (Kosong/Standar)
def_name = "XX"
def_brand_idx = 1 # astral_at
def_glass_idx = 1 # clear_8mm
def_qty = 1
def_w = 100
def_h = 100
def_vendor_tot = 1000000

# 2. Kalau Lampu Sein Edit Nyala, Ganti Nilai Default pakai data lama
if is_edit_mode:
    item_lama = st.session_state["keranjang_proyek"][edit_idx]
    def_name = item_lama["meta"]["nama_item"]
    
    # Mapping nama ke urutan list (Biar dropdownnya pas)
    brand_list = ["astral_ap", "astral_at", "astral_as", "astral_lm", "ykk_nexta"]
    glass_list = [
        "clear_5mm", "clear_6mm", "clear_8mm", "clear_10mm", 
        "clear_8mm_jumbo", "clear_10mm_jumbo", "tempered_6mm", 
        "tempered_8mm", "dania_glass", "sandblast_10mm", 
        "sandblast_8mm", "laminated_5+5_mm", "insulated_5+A10+5mm", 
        "non_glass"
    ]    
    old_brand = item_lama["meta"].get("brand_name", item_lama["meta"].get("brand_used", "astral_ap"))
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
        glass = st.selectbox("Jenis Kaca", [
            "clear_5mm", "clear_6mm", "clear_8mm", "clear_10mm", 
            "clear_8mm_jumbo", "clear_10mm_jumbo", "tempered_6mm", 
            "tempered_8mm", "dania_glass", "sandblast_10mm", 
            "sandblast_8mm", "laminated_5+5_mm", "insulated_5+A10+5mm", 
            "non_glass"
        ], index=def_glass_idx)
        
    with col2:
        qty = st.number_input("Quantity (Jumlah Lubang)", min_value=1, value=def_qty)
        width = st.number_input("Lebar Jendela (cm)", min_value=10, value=def_w)
        height = st.number_input("Tinggi Jendela (cm)", min_value=10, value=def_h)
        
    with col3:
        # input harga vendor total, bukan satuan
        vendor_price_total = st.number_input("Harga Modal Vendor (TOTAL KESELURUHAN)", min_value=0, value=def_vendor_tot, step=100000)
        # --- 🟢 FITUR BARU: SMART OVERRIDE MULTIPLIER 🟢 ---
        import json
        try:
            with open("pricing.json", "r") as f:
                data_harga = json.load(f)
            # Ambil angka default dari JSON berdasarkan brand yang lagi dipilih di col1
            # Contoh: kalau milih 'astral_at', angka_bawaan jadi 2.85
            angka_bawaan = data_harga["aluminum_multipliers"].get(brand, 2.2) 
        except:
            angka_bawaan = 2.2 # Angka jaga-jaga kalau JSON error
            
        # Tampilkan di UI dengan nilai default dari JSON
        custom_multiplier = st.number_input("Multiplier Harga Jual (Markup)", value=float(angka_bawaan), step=0.1)
        # ----------------------------------------------------
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
# BAGIAN 2: TABEL KERANJANG (HYBRID CUSTOM COLUMNS + SPEK)
# ==========================================
st.header(f"2. Rincian Proyek ({len(st.session_state['keranjang_proyek'])} Item)")

if len(st.session_state["keranjang_proyek"]) > 0:
    # 11 Kolom biar muat spek text area
    kolom_rasio = [0.5, 1.2, 3.0, 0.8, 1, 1.5, 0.8, 0.8, 1.5, 1.5, 1.2]
    
    t_cols = st.columns(kolom_rasio)
    t_cols[0].write("**No**")
    t_cols[1].write("**Item**")
    t_cols[2].write("**Spesifikasi (Edit)**") # Kolom Baru
    t_cols[3].write("**Qty**")
    t_cols[4].write("**Brand**")
    t_cols[5].write("**Kaca**")
    t_cols[6].write("**L(m)**")
    t_cols[7].write("**T(m)**")
    t_cols[8].write("**Satuan**")
    t_cols[9].write("**Total**")
    t_cols[10].write("**Aksi**")
    st.divider()
    
    for i, item in enumerate(st.session_state["keranjang_proyek"]):
        c = st.columns(kolom_rasio)
        c[0].write(i + 1)
        c[1].write(item["meta"]["nama_item"])
        
        # --- LOGIKA KOLOM SPESIFIKASI DINAMIS ---
        if "spek_custom" not in item["meta"]:
            tipe_kaca_cantik = str(item["meta"]["glass_used"]).replace("_", " ").title()
            brand_cantik = str(item["meta"]["brand_used"]).replace("_", " ").title()
            # 🟢 FITUR KACA (NON GLASS OR NO): Biar bahasanya masuk akal
            if item["meta"]["glass_used"] == "non_glass":
                baris_kaca = "- Tanpa Kaca\n"
            else:
                baris_kaca = f"- Kaca {tipe_kaca_cantik}\n"
            template_default = (
                f"- {brand_cantik} Fixed Window\n"
                f"- VC-03\n"
                f"- Warna Monochromatic\n"
                f"{baris_kaca}" #ngambil dari fitur atas. 
                f"- Sealant\n"
                f"- Instalasi\n"
                f"Dimensi : {item['meta']['width_cm']}X{item['meta']['height_cm']}" 
            )
            item["meta"]["spek_custom"] = template_default

        # Text Area yang bisa diedit
        spek_baru = c[2].text_area("Spek", value=item["meta"]["spek_custom"], key=f"spek_{i}", height=140, label_visibility="collapsed")
        
        # Save kalau ada perubahan
        if spek_baru != item["meta"]["spek_custom"]:
            item["meta"]["spek_custom"] = spek_baru
            st.rerun()
            
        # --- DATA LAINNYA ---
        c[3].write(item["meta"]["quantity"])
        c[4].write(item["meta"]["brand_used"].replace("astral_", "").upper())
        c[5].write(item["meta"]["glass_used"].replace("_"," ").upper())
        c[6].write(item["meta"]["width_m"])
        c[7].write(item["meta"]["height_m"])
        c[8].write(f"Rp {item['selling']['unit_price']:,.0f}")
        c[9].write(f"Rp {item['selling']['total_price']:,.0f}")
        
        with c[10]:
            act1, act2 = st.columns(2)
            if act1.button("✏️", key=f"edit_{i}"):
                st.session_state["edit_index"] = i
                st.session_state["scroll_up"] = True # NYALAKAN PERINTAH SCROLL!
                st.rerun()
            if act2.button("🗑️", key=f"del_{i}"):
                st.session_state["keranjang_proyek"].pop(i)
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
# BAGIAN 3: NEGOSIASI & TOTAL (AUTO-CALCULATE)
# ==========================================
if len(st.session_state["keranjang_proyek"]) > 0:
    st.header("3. Detail rinci & Profitabilitas Proyek")

    pilihan_perusahaan = st.selectbox("🏢 Gunakan Bendera Perusahaan:", 
                                      ["Angkasa Bangunan Jakarta", "Cahaya Kaca Kreatif", "Angkasa Bangunan", "ERI"])
    
    # 🟢 2. LOGIKA PAJAK: ABJ kena pajak, sisanya bebas
    kena_ppn = True if pilihan_perusahaan == "Angkasa Bangunan Jakarta" else False
    #Notif
    if kena_ppn:
        st.info("ℹ️ Status PKP: Perhitungan margin otomatis dipotong setoran PPN 11%.")
    else:
        st.success("ℹ️ Status Non-PKP: Margin bersih, tidak ada potongan PPN.")

    col4, col5 = st.columns(2)

    with col4:
        my_discount = st.slider("Diskon Proyek ke Client (%)", min_value=0, max_value=50, value=35)
    with col5:
        arch_fee = st.slider("Fee Arsitek/Kontraktor (%)", min_value=0, max_value=20, value=0)

    # 🟢 TOMBOL DIHAPUS, LANGSUNG NGITUNG OTOMATIS
    profit_analysis = analyze_profitability(st.session_state["keranjang_proyek"], my_discount, arch_fee, kena_ppn)
    st.success("Kalkulasi Total Proyek Otomatis Diperbarui!")
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric(label="Grand Total", value=f"Rp {profit_analysis['grand_list_price']:,.0f}")
    m2.metric(label="Deal Klien (after disc)", value=f"Rp {profit_analysis['final_price']:,.0f}")
    m3.metric(label="Total Modal Proyek (COGS)", value=f"Rp {profit_analysis['total_base_cost']:,.0f}")
    m4.metric(label="Profit Bersih Proyek", 
                value=f"Rp {profit_analysis['gross_income']:,.0f}", 
                delta=f"{profit_analysis['margin_percent']}% Margin",
                delta_color="normal" if profit_analysis['margin_percent'] >= 15 else "inverse")
    
    # # Rincian Jual 
    # st.divider()
    # st.write("**🧾 Rincian Total Harga Jual Proyek (Material & Tenaga):**")
    # tot_alum_jual = sum(item["selling"]["breakdown"]["alum"] for item in st.session_state["keranjang_proyek"])
    # tot_kaca_jual = sum(item["selling"]["breakdown"].get("glass", 0) for item in st.session_state["keranjang_proyek"])
    # tot_sealant_jual = sum(item["selling"]["breakdown"].get("sealant", 0) for item in st.session_state["keranjang_proyek"])

    # col_m1, col_m2, col_m3= st.columns(3)
    # col_m1.metric("Jual Alumunium", f"Rp {tot_alum_jual:,.0f}")
    # col_m2.metric("Jual Kaca", f"Rp {tot_kaca_jual:,.0f}")
    # col_m3.metric("Jual Sealant", f"Rp {tot_sealant_jual:,.0f}")
   
    
    
    # # Rincian Modal
    # st.divider()
    # st.write("**📦 Rincian Total Modal Proyek (Material & Tenaga):**")
    # tot_alum = sum(item["costing"]["vendor_base_total"] for item in st.session_state["keranjang_proyek"])
    # tot_kaca = sum(item["costing"].get("kaca_base_cost", 0) for item in st.session_state["keranjang_proyek"])
    # tot_sealant = sum(item["costing"].get("sealant_base_cost", 0) for item in st.session_state["keranjang_proyek"])
    # tot_tenaga = sum(item["costing"].get("manpower_base_cost", 0) for item in st.session_state["keranjang_proyek"])

    # col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    # col_m1.metric("Modal Alumunium", f"Rp {tot_alum:,.0f}")
    # col_m2.metric("Modal Kaca", f"Rp {tot_kaca:,.0f}")
    # col_m3.metric("Modal Sealant", f"Rp {tot_sealant:,.0f}")
    # col_m4.metric("Tenaga Tukang", f"Rp {tot_tenaga:,.0f}")

    # st.divider()
    # st.write("**Detail Transparansi Pajak & Diskon:**")
    # st.write(f"- Total RAB Awal (Kasar): Rp {profit_analysis['grand_list_price']:,.0f}")
    # st.write(f"- Total Diskon ({my_discount}%): Rp {profit_analysis['debug']['discount_amount']:,.0f}")
    # st.write(f"- Selisih PPN Disetor: Rp {profit_analysis['debug']['ppn_diff']:,.0f}")
    # ==========================================
    # RINCIAN TOTAL HARGA JUAL (UI DIPERKECIL)
    # ==========================================
    st.markdown("---")
    st.write("##### 🧾 Rincian Total Harga Jual Proyek (Material & Tenaga)")
    
    # 🟢 KEMBALI KE RUMUS ASLI LU: Karena di engine udah dikali qty
    tot_alum_jual = sum(item["selling"]["breakdown"]["alum"] for item in st.session_state["keranjang_proyek"])
    tot_kaca_jual = sum(item["selling"]["breakdown"].get("glass", 0) for item in st.session_state["keranjang_proyek"])
    tot_sealant_jual = sum(item["selling"]["breakdown"].get("sealant", 0) for item in st.session_state["keranjang_proyek"])

    # 🟢 UI BOX / CONTAINER 
    with st.container(border=True):
        rc1, rc2, rc3 = st.columns(3)
        with rc1:
            st.caption("Jual Alumunium")
            st.markdown(f"**Rp {tot_alum_jual:,.0f}**")
        with rc2:
            st.caption("Jual Kaca")
            st.markdown(f"**Rp {tot_kaca_jual:,.0f}**")
        with rc3:
            st.caption("Jual Sealant")
            st.markdown(f"**Rp {tot_sealant_jual:,.0f}**")
    
    # ==========================================
    # RINCIAN TOTAL MODAL (UI DIPERKECIL)
    # ==========================================
    st.write("##### 📦 Rincian Total Modal Proyek (COGS)")
    
    tot_alum = sum(item["costing"]["vendor_base_total"] for item in st.session_state["keranjang_proyek"])
    tot_kaca = sum(item["costing"].get("kaca_base_cost", 0) for item in st.session_state["keranjang_proyek"])
    tot_sealant = sum(item["costing"].get("sealant_base_cost", 0) for item in st.session_state["keranjang_proyek"])
    tot_tenaga = sum(item["costing"].get("manpower_base_cost", 0) for item in st.session_state["keranjang_proyek"])

    with st.container(border=True):
        mc1, mc2, mc3, mc4 = st.columns(4)
        with mc1:
            st.caption("Modal Alumunium")
            st.markdown(f"**Rp {tot_alum:,.0f}**")
        with mc2:
            st.caption("Modal Kaca")
            st.markdown(f"**Rp {tot_kaca:,.0f}**")
        with mc3:
            st.caption("Modal Sealant")
            st.markdown(f"**Rp {tot_sealant:,.0f}**")
        with mc4:
            st.caption("Tenaga Tukang")
            st.markdown(f"**Rp {tot_tenaga:,.0f}**")




    # ==========================================
    # BAGIAN 4: DATA KLIEN & CETAK PDF
    # ==========================================
    st.markdown("---")
    st.header("4. Data Klien & Cetak Penawaran")
    
    with st.container(border=True):
        

        #Baris 2 : Data Customer 
        c_klien1, c_klien2 = st.columns(2)
        with c_klien1:
            nama_klien = st.text_input("Nama Customer", placeholder="Cth: Bp. Hengky")
            lokasi_klien = st.text_input("Lokasi Proyek", placeholder="Cth: Jakarta")
            no_quotation = st.text_input("No. Penawaran", placeholder="Cth: QUO/2026/02/001")

        with c_klien2:
            default_note = """- Harga sudah termasuk instalasi diluar pekerjaan sipil (bobok dan plester)
-  Gudang, listrik dan scafolding disediakan oleh pemberi pekerjaan
- Garansi warna 10 tahun dan hardware 1 tahun
- Waktu produksi pabrikasi 40 - 65 hari kerja dari ACC Shopdrawing
- DP 50% diawal pengerjaan
- Pembayaran 40% sebelum barang terkirim 
- Pembayaran 10% setelah pekerjaan selesai
- Perubahan yang terjadi akibat adanya perubahan gambar detail/penyempurnaan struktur/perubahan desain dsb, akan diperhitungkan dalam surat revisi penawaran
- Pembayaran pelunasan maksimal dilakukan 30 hari setelah serah terima dilakukan. Jika customer tidak dapat memenuhi kewajiban tsb maka aplikator berhak mengambil kembali barang yang telah terpasang 
-  Batas maksimum penitipan barang di gudang 1 bulan dari timeline pekerjaan awal. Setelahnya akan dikenakan biaya sewa gudang
- Penawaran ini berlaku 14 hari setelah dibuat."""
            note_tambahan = st.text_area("Note / Syarat & Ketentuan", value=default_note, height=235)
    
    # Siapkan data untuk dikirim ke pdf_maker.py
    client_data = {
        "perusahaan": pilihan_perusahaan, # 👈 Ngirim nama PT ke mesin PDF
        "no_quo": no_quotation if no_quotation else "-",
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