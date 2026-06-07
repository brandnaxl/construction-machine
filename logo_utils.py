"""
Logo loading, auto-trimming, and dimension helpers for PDF and XLSX output.

Trim logic:
  - RGBA / LA PNG: crop to the alpha-channel bounding box (transparent background).
  - RGB / other:   crop by comparing to a pure-white background; pixels within
                   _WHITE_THRESHOLD of (255,255,255) are treated as background.
"""

import io
import os

try:
    from PIL import Image, ImageChops
    _PILLOW = True
except ImportError:
    _PILLOW = False

_WHITE_THRESHOLD = 10   # distance from pure white that counts as "background"


def _trim(img: "Image.Image") -> "Image.Image":
    if img.mode in ("RGBA", "LA"):
        alpha = img.split()[-1]
        bbox  = alpha.getbbox()
    else:
        rgb  = img.convert("RGB")
        bg   = Image.new("RGB", rgb.size, (255, 255, 255))
        diff = ImageChops.difference(rgb, bg)
        diff = diff.point(lambda p: 255 if p > _WHITE_THRESHOLD else 0)
        bbox = diff.convert("L").getbbox()
    return img.crop(bbox) if bbox else img


def load_trimmed(path: str):
    """Return a trimmed PIL Image, or None if unavailable."""
    if not _PILLOW or not path or not os.path.exists(path):
        return None
    try:
        return _trim(Image.open(path))
    except Exception:
        return None


def to_bytes(img) -> io.BytesIO | None:
    """Serialize a PIL Image to a PNG BytesIO buffer."""
    if img is None:
        return None
    buf = io.BytesIO()
    out = img if img.mode in ("RGB", "RGBA") else img.convert("RGB")
    out.save(buf, format="PNG")
    buf.seek(0)
    return buf


def pdf_logo_w(img, target_h_mm: float) -> float:
    """Return the proportional width (mm) for a logo rendered at target_h_mm."""
    w, h = img.size
    return target_h_mm * w / h


def xlsx_logo_dims(img, target_h_px: int) -> tuple[int, int]:
    """Return (width_px, height_px) scaled to target_h_px."""
    w, h = img.size
    return int(target_h_px * w / h), target_h_px
