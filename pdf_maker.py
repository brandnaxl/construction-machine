import os
from fpdf import FPDF
import datetime

_LOGOS_DIR = os.path.join(os.path.dirname(__file__), "Templates", "Logos")

# ==========================================
# 1. DATABASE PROFIL PERUSAHAAN (MULTI-TENANT)
# ==========================================
PROFIL_PERUSAHAAN = {
    "Angkasa Bangunan": {
        "logo_kiri": os.path.join(_LOGOS_DIR, "angkasa bangunan.png"),
        "nama": "ANGKASA BANGUNAN",
        "tagline": "Specialist Aluminium & Kaca",
        "alamat": "Jl. Contoh Alamat No. 123, Jakarta Barat"
    },
    "Cahaya Kaca Kreatif": {
        "logo_kiri": os.path.join(_LOGOS_DIR, "ckk logo.png"),
        "nama": "PT. CAHAYA KACA KREATIF",
        "tagline": "Applicator Astral Aluminium Systems",
        "alamat": "Jl. Pegangsaan Dua, Kelapa Gading, Jakarta Utara"
    },
    "ABJ": {
        "logo_kiri": "",
        "nama": "PT. ALUMUNIUM BANGUN JAYA (ABJ)",
        "tagline": "General Contractor & Aluminium Specialist",
        "alamat": "Jl. Panjang No. 8, Jakarta Barat"
    },
    "ERI": {
        "logo_kiri": "",
        "nama": "ERI ALUMINIUM",
        "tagline": "Premium Windows & Doors",
        "alamat": "Jl. Sudirman No. 1, Jakarta Pusat"
    }
}

# ==========================================
# 2. TEMPLATE KERTAS & HEADER DINAMIS
# ==========================================
class PDFMaker(FPDF):
    def __init__(self, profil, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.profil = profil # Simpan profil PT yang dipilih ke dalam memori PDF

    def header(self):
        # Logo kiri (perusahaan) — diperbesar 4x
        if os.path.exists(self.profil["logo_kiri"]):
            self.image(self.profil["logo_kiri"], 10, 5, 88)

        # Logo kanan (Astral) — diperbesar 4x, mepet kanan
        _astral = os.path.join(_LOGOS_DIR, "astral.png")
        if os.path.exists(_astral):
            self.image(_astral, 112, 5, 88)

        # Posisikan kursor di bawah logo (logo 88mm mulai dari y=5)
        self.set_y(96)

        # Garis pembatas tebal
        self.set_draw_color(0, 0, 0)
        self.set_line_width(1.5)
        self.line(10, self.get_y(), 200, self.get_y())
        self.set_line_width(0.2)  # reset ke default
        self.ln(10)

# ==========================================
# 3. MESIN UTAMA GENERATOR INVOICE
# ==========================================
def generate_quotation_pdf(keranjang, profit_analysis, client_data):
    # Ambil data PT sesuai pilihan di Streamlit
    profil_terpilih = PROFIL_PERUSAHAAN.get(client_data["perusahaan"], PROFIL_PERUSAHAAN["Angkasa Bangunan"])
    
    pdf = PDFMaker(profil=profil_terpilih, orientation='P', unit='mm', format='A4')
    pdf.add_page()
    
    # --- DATA KLIEN, TANGGAL & NO QUOTATION ---
    pdf.set_font('helvetica', 'B', 10)
    
    # BARIS 1: Kepada Yth (Kiri) & No Quotation (Kanan)
    pdf.cell(130, 5, 'Kepada Yth.', 0, 0)
    pdf.cell(60, 5, f'{client_data["no_quo"]}', 0, 1, 'R') 
    
    # BARIS 2: Nama Klien (Kiri) & Tanggal (Kanan)
    tgl_sekarang = datetime.datetime.now().strftime("%d %B %Y")
    pdf.set_font('helvetica', '', 10)
    pdf.cell(130, 5, f'{client_data["nama"]}', 0, 0) 
    pdf.cell(60, 5, f'Jakarta, {tgl_sekarang}', 0, 1, 'R') 
    
    # BARIS 3: Lokasi Proyek (Kiri)
    pdf.cell(130, 5, f'{client_data["lokasi"]}', 0, 1)
    
    pdf.ln(5)
    pdf.cell(0, 5, 'Dengan ini kami sertakan penawaran produk kami sesuai dengan gambar kerja yang dikirimkan kepada kami.', 0, 1)
    pdf.ln(5)
    
    # --- TABEL DATA ---
    pdf.set_font("helvetica", "B", 9)
    with pdf.table(borders_layout="ALL", text_align="CENTER", col_widths=(10, 20, 70, 15, 35, 40)) as table:
        row = table.row()
        for header in ["No", "Item", "Spesifikasi", "Unit", "Harga/Unit", "Harga"]:
            row.cell(header)
            
        pdf.set_font("helvetica", "", 9)
        for i, item in enumerate(keranjang):
            row = table.row()
            row.cell(str(i + 1))
            row.cell(item["meta"]["nama_item"])
            
            # Ambil Spek yang udah diedit di web
            spek_text = item["meta"].get("spek_custom", "-")
            row.cell(spek_text, align="L")
            
            row.cell(str(item["meta"]["quantity"]))
            row.cell(f"Rp {item['selling']['unit_price']:,.0f}", align="C")
            row.cell(f"Rp {item['selling']['total_price']:,.0f}", align="C")

    # --- TOTAL & DISKON ---
    pdf.set_font("helvetica", "B", 6)
    pdf.cell(115) 
    pdf.cell(35, 7, "TOTAL HARGA", border=1, align="C")
    pdf.cell(40, 7, f"Rp {profit_analysis['grand_list_price']:,.0f}", border=1, align="R", ln=1)
    
    pdf.cell(115)
    pdf.cell(35, 7, f"DISKON {client_data['diskon_persen']}%", border=1, align="C")
    pdf.cell(40, 7, f"Rp {profit_analysis['debug']['discount_amount']:,.0f}", border=1, align="R", ln=1)
    
    pdf.cell(115)
    pdf.set_fill_color(255, 255, 0)
    pdf.cell(35, 7, "TOTAL SETELAH DISKON", border=1, align="C", fill=True)
    pdf.cell(40, 7, f"Rp {profit_analysis['final_price']:,.0f}", border=1, align="R", fill=True, ln=1)
    
    # --- NOTE T&C ---
    pdf.ln(10)
    pdf.set_font("helvetica", "B", 9)
    pdf.cell(0, 5, "Note:", 0, 1)
    pdf.set_font("helvetica", "", 8)
    pdf.multi_cell(0, 5, client_data["note"])
    
    # --- TANDA TANGAN (POSISI DIUBAH MAKIN KIRI) ---
    pdf.ln(15)
    pdf.set_font("helvetica", "", 10)
    
    # Bikin 2 kolom imajiner (Kiri 60mm, Kosong 70mm, Kanan 60mm)
    pdf.cell(60, 5, "Disetujui Oleh", 0, 0, 'C')
    pdf.cell(70, 5, "", 0, 0) # Jarak di tengah
    pdf.cell(60, 5, "Hormat Kami,", 0, 1, 'C')
    
    pdf.ln(20) # Jarak buat tanda tangan pulpen
    pdf.cell(60, 5, "(                                  )", 0, 0, 'C')
    pdf.cell(70, 5, "", 0, 0)
    pdf.cell(60, 5, f"{profil_terpilih['nama']}", 0, 1, 'C')

    return bytes(pdf.output())