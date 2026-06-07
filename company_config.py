import os

_LOGOS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Templates", "Logos")

COMPANIES = {
    "Angkasa Bangunan Jakarta": {
        "key":               "ABJ",
        "is_pkp":            True,
        "logo":              "angkasa bangunan.png",
        "nama":              "PT. ANGKASA BANGUNAN JAKARTA",
        "tagline":           "Specialist Aluminium & Kaca",
        "alamat":            "Jl. Panjang No. 8, Jakarta Barat",
        "header_fill":       "D9D9D9",
        "header_font_color": "000000",
    },
    "Angkasa Bangunan": {
        "key":               "AB",
        "is_pkp":            False,
        "logo":              "angkasa bangunan.png",
        "nama":              "ANGKASA BANGUNAN",
        "tagline":           "Specialist Aluminium & Kaca",
        "alamat":            "Jl. Contoh Alamat No. 123, Jakarta Barat",
        "header_fill":       "D9D9D9",
        "header_font_color": "000000",
    },
    "PT. Cahaya Kaca Kreatif": {
        "key":               "CKK",
        "is_pkp":            False,
        "logo":              "ckk logo.png",
        "nama":              "PT. CAHAYA KACA KREATIF",
        "tagline":           "Applicator Astral Aluminium Systems",
        "alamat":            "Jl. Pegangsaan Dua, Kelapa Gading, Jakarta Utara",
        "header_fill":       "595959",
        "header_font_color": "FFFFFF",
    },
    "ERI Aluminium": {
        "key":               "ERI",
        "is_pkp":            False,
        "logo":              "",
        "nama":              "ERI ALUMINIUM",
        "tagline":           "Premium Windows & Doors",
        "alamat":            "Jl. Sudirman No. 1, Jakarta Pusat",
        "header_fill":       "D9D9D9",
        "header_font_color": "000000",
    },
}

COMPANY_NAMES = list(COMPANIES.keys())

ASTRAL_LOGO_PATH = os.path.join(_LOGOS_DIR, "astral.png")


def get_company(display_name: str) -> dict:
    """Return company config dict; falls back to first entry if name unknown."""
    return COMPANIES.get(display_name, COMPANIES[COMPANY_NAMES[0]])


def logo_path(display_name: str) -> str:
    """Return absolute path to company logo file, or '' if none configured."""
    filename = get_company(display_name).get("logo", "")
    if not filename:
        return ""
    return os.path.join(_LOGOS_DIR, filename)
