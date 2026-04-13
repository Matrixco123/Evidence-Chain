import os
from pathlib import Path
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image


REPORT_DIR = Path(__file__).resolve().parent / "tamper_reports"
REPORT_DIR.mkdir(exist_ok=True)


def _fit_image_size(image_path, max_width, max_height):
    """Return (width, height) that fits the image within the given bounds
    while preserving aspect ratio."""
    img = Image.open(image_path)
    img_w, img_h = img.size
    ratio = min(max_width / img_w, max_height / img_h)
    return img_w * ratio, img_h * ratio


def _draw_section_title(c, title, y, page_width):
    """Draw a styled section heading and return the updated y position."""
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(HexColor("#1e293b"))
    c.drawString(60, y, title)

    # Underline
    c.setStrokeColor(HexColor("#3b82f6"))
    c.setLineWidth(1.5)
    c.line(60, y - 4, page_width - 60, y - 4)

    c.setFillColor(HexColor("#000000"))
    return y - 24


def _draw_centered_image(c, image_path, y, page_width, max_w=4.5 * inch, max_h=3 * inch):
    """Draw an image centered on the page and return the updated y position."""
    w, h = _fit_image_size(image_path, max_w, max_h)
    x = (page_width - w) / 2
    y -= h
    c.drawImage(ImageReader(image_path), x, y, width=w, height=h,
                preserveAspectRatio=True, mask="auto")
    return y - 16


def _next_report_path(record_id: int) -> Path:
    """Return the next available report path for a given record ID.

    First call  -> tamper_reports/tampered_report_26.pdf
    Second call -> tamper_reports/tampered_report_26(1).pdf
    Third call  -> tamper_reports/tampered_report_26(2).pdf  …and so on.
    """
    base = REPORT_DIR / f"tampered_report_{record_id}.pdf"
    if not base.exists():
        return base
    counter = 1
    while True:
        candidate = REPORT_DIR / f"tampered_report_{record_id}({counter}).pdf"
        if not candidate.exists():
            return candidate
        counter += 1


def generate_tamper_report(record_id, original_path, tampered_path, diff_path):
    """Generate a Tamper Analysis Report PDF.

    Parameters
    ----------
    record_id : int
        The database record ID for this evidence.
    original_path : str
        Path to the original (certified) evidence file.
    tampered_path : str
        Path to the submitted (potentially tampered) evidence file.
    diff_path : str
        Path to the diff/difference visualisation image.

    Returns
    -------
    str
        Full absolute path to the generated PDF report.
    """
    output_path = str(_next_report_path(record_id))

    page_w, page_h = letter
    c = canvas.Canvas(output_path, pagesize=letter)

    # ── Header bar ──────────────────────────────────────────────────────
    c.setFillColor(HexColor("#0f172a"))
    c.rect(0, page_h - 80, page_w, 80, fill=True, stroke=False)

    c.setFillColor(HexColor("#ffffff"))
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(page_w / 2, page_h - 40, "EVIDENCE TAMPER ANALYSIS REPORT")

    c.setFont("Helvetica", 9)
    c.setFillColor(HexColor("#94a3b8"))
    c.drawCentredString(page_w / 2, page_h - 58, f"Generated: {datetime.now().strftime('%Y-%m-%d  %H:%M:%S')}")

    # ── Accent line ─────────────────────────────────────────────────────
    c.setStrokeColor(HexColor("#3b82f6"))
    c.setLineWidth(3)
    c.line(0, page_h - 82, page_w, page_h - 82)

    y = page_h - 110

    # ── Section A: Original Evidence ────────────────────────────────────
    y = _draw_section_title(c, "A.  Original Evidence", y, page_w)
    if os.path.exists(original_path):
        y = _draw_centered_image(c, original_path, y, page_w)
    else:
        c.setFont("Helvetica-Oblique", 10)
        c.setFillColor(HexColor("#ef4444"))
        c.drawString(80, y, f"[File not found: {original_path}]")
        y -= 20
        c.setFillColor(HexColor("#000000"))

    # ── Section B: Submitted Evidence ───────────────────────────────────
    y = _draw_section_title(c, "B.  Submitted Evidence", y, page_w)
    if os.path.exists(tampered_path):
        y = _draw_centered_image(c, tampered_path, y, page_w)
    else:
        c.setFont("Helvetica-Oblique", 10)
        c.setFillColor(HexColor("#ef4444"))
        c.drawString(80, y, f"[File not found: {tampered_path}]")
        y -= 20
        c.setFillColor(HexColor("#000000"))

    # ── New page for diff + conclusion ──────────────────────────────────
    c.showPage()
    y = page_h - 60

    # ── Section C: Detected Differences ─────────────────────────────────
    y = _draw_section_title(c, "C.  Detected Differences", y, page_w)
    if os.path.exists(diff_path):
        y = _draw_centered_image(c, diff_path, y, page_w, max_h=4 * inch)
    else:
        c.setFont("Helvetica-Oblique", 10)
        c.setFillColor(HexColor("#ef4444"))
        c.drawString(80, y, f"[File not found: {diff_path}]")
        y -= 20
        c.setFillColor(HexColor("#000000"))

    y -= 20

    # ── Section D: Conclusion ───────────────────────────────────────────
    y = _draw_section_title(c, "D.  Conclusion", y, page_w)

    # Red warning box
    box_x, box_w, box_h = 50, page_w - 100, 50
    c.setFillColor(HexColor("#fef2f2"))
    c.setStrokeColor(HexColor("#ef4444"))
    c.setLineWidth(1)
    c.roundRect(box_x, y - box_h, box_w, box_h, 6, fill=True, stroke=True)

    c.setFillColor(HexColor("#b91c1c"))
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(page_w / 2, y - 30,
                        "This evidence has been modified after certification.")

    y -= box_h + 30

    # ── Footer ──────────────────────────────────────────────────────────
    c.setFillColor(HexColor("#64748b"))
    c.setFont("Helvetica", 8)
    c.drawCentredString(page_w / 2, 30,
                        "EvidenceChain  •  Digital Evidence Verification System")

    c.save()
    return output_path
