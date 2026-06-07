import os
import io
import datetime
from fpdf import FPDF
import company_config
from logo_utils import load_trimmed, to_bytes as _logo_bytes, pdf_logo_w

_LOGO_Y    = 5    # mm from top of page
_LOGO_H    = 16   # mm — fixed height for all logos
_DIVIDER_Y = 26   # _LOGO_Y + _LOGO_H + 5 padding
_CONTENT_Y = 36   # _DIVIDER_Y + 10


class PDFMaker(FPDF):
    def __init__(self, company_name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.profil       = company_config.get_company(company_name)
        self._logo_path   = company_config.logo_path(company_name)
        self._astral_path = company_config.ASTRAL_LOGO_PATH

    def header(self):
        # Company logo — trimmed, fixed height, width auto from aspect ratio
        co_img = load_trimmed(self._logo_path)
        if co_img:
            self.image(_logo_bytes(co_img), x=10, y=_LOGO_Y, h=_LOGO_H)
        elif self._logo_path and os.path.exists(self._logo_path):
            self.image(self._logo_path, x=10, y=_LOGO_Y, h=_LOGO_H)

        # Partner logo — trimmed, right-aligned at x=200
        as_img = load_trimmed(self._astral_path)
        if as_img:
            as_w = pdf_logo_w(as_img, _LOGO_H)
            self.image(_logo_bytes(as_img), x=200 - as_w, y=_LOGO_Y, h=_LOGO_H)
        elif os.path.exists(self._astral_path):
            self.image(self._astral_path, x=160, y=_LOGO_Y, h=_LOGO_H)

        # Divider line
        self.set_y(_DIVIDER_Y)
        self.set_draw_color(0, 0, 0)
        self.set_line_width(1.5)
        self.line(10, _DIVIDER_Y, 200, _DIVIDER_Y)
        self.set_line_width(0.2)
        self.set_y(_CONTENT_Y)


def generate_quotation_pdf(keranjang, profit_analysis, client_data):
    profil = company_config.get_company(client_data["perusahaan"])

    pdf = PDFMaker(company_name=client_data["perusahaan"],
                   orientation='P', unit='mm', format='A4')
    pdf.add_page()

    # --- CLIENT INFO & DATE ---
    pdf.set_font('helvetica', 'B', 10)
    pdf.cell(130, 5, 'Kepada Yth.', 0, 0)
    pdf.cell(60, 5, f'{client_data["no_quo"]}', 0, 1, 'R')

    tgl_sekarang = datetime.datetime.now().strftime("%d %B %Y")
    pdf.set_font('helvetica', '', 10)
    pdf.cell(130, 5, f'{client_data["nama"]}', 0, 0)
    pdf.cell(60, 5, f'Jakarta, {tgl_sekarang}', 0, 1, 'R')
    pdf.cell(130, 5, f'{client_data["lokasi"]}', 0, 1)

    pdf.ln(5)
    pdf.cell(0, 5,
             'Dengan ini kami sertakan penawaran produk kami sesuai dengan '
             'gambar kerja yang dikirimkan kepada kami.', 0, 1)
    pdf.ln(5)

    # --- ITEM TABLE ---
    pdf.set_font("helvetica", "B", 9)
    with pdf.table(borders_layout="ALL", text_align="CENTER",
                   col_widths=(10, 20, 70, 15, 35, 40)) as table:
        row = table.row()
        for header in ["No", "Item", "Spesifikasi", "Unit", "Harga/Unit", "Harga"]:
            row.cell(header)

        pdf.set_font("helvetica", "", 9)
        for i, item in enumerate(keranjang):
            row = table.row()
            row.cell(str(i + 1))
            row.cell(item["meta"]["nama_item"])
            row.cell(item["meta"].get("spek_custom", "-"), align="L")
            row.cell(str(item["meta"]["quantity"]))
            row.cell(f"Rp {item['selling']['unit_price']:,.0f}", align="C")
            row.cell(f"Rp {item['selling']['total_price']:,.0f}", align="C")

    # --- TOTALS ---
    pdf.set_font("helvetica", "B", 6)
    pdf.cell(115)
    pdf.cell(35, 7, "TOTAL HARGA", border=1, align="C")
    pdf.cell(40, 7, f"Rp {profit_analysis['grand_list_price']:,.0f}",
             border=1, align="R", ln=1)

    pdf.cell(115)
    pdf.cell(35, 7, f"DISKON {client_data['diskon_persen']}%", border=1, align="C")
    pdf.cell(40, 7, f"Rp {profit_analysis['debug']['discount_amount']:,.0f}",
             border=1, align="R", ln=1)

    pdf.cell(115)
    pdf.set_fill_color(255, 255, 0)
    pdf.cell(35, 7, "TOTAL SETELAH DISKON", border=1, align="C", fill=True)
    pdf.cell(40, 7, f"Rp {profit_analysis['final_price']:,.0f}",
             border=1, align="R", fill=True, ln=1)

    # --- NOTES ---
    pdf.ln(10)
    pdf.set_font("helvetica", "B", 9)
    pdf.cell(0, 5, "Note:", 0, 1)
    pdf.set_font("helvetica", "", 8)
    pdf.multi_cell(0, 5, client_data["note"])

    # --- SIGNATURE ---
    pdf.ln(15)
    pdf.set_font("helvetica", "", 10)
    pdf.cell(60, 5, "Disetujui Oleh", 0, 0, 'C')
    pdf.cell(70, 5, "", 0, 0)
    pdf.cell(60, 5, "Hormat Kami,", 0, 1, 'C')
    pdf.ln(20)
    pdf.cell(60, 5, "(                                  )", 0, 0, 'C')
    pdf.cell(70, 5, "", 0, 0)
    pdf.cell(60, 5, profil['nama'], 0, 1, 'C')

    return bytes(pdf.output())
