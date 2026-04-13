from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime

def generate_pdf(filename, hash_val, qr_path, signature="", output_path="certificate.pdf"):
    c = canvas.Canvas(output_path, pagesize=letter)
    
    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(150, 750, "EvidenceChain")
    
    c.setFont("Helvetica", 12)
    c.drawString(150, 730, "Digital Evidence Certificate")
    
    # File details
    c.drawString(100, 680, f"Filename: {filename}")
    c.drawString(100, 660, f"SHA-256 Hash:")
    
    # Split hash for readability
    c.setFont("Courier", 8)
    c.drawString(100, 640, hash_val[:64])
    
    c.setFont("Helvetica", 12)
    c.drawString(100, 600, f"Timestamp: {datetime.now()}")
    
    # Digital Signature
    if signature:
        c.drawString(100, 570, "Digital Signature:")
        c.setFont("Courier", 6)
        # Wrap long signature across multiple lines
        chars_per_line = 90
        y = 555
        for i in range(0, len(signature), chars_per_line):
            c.drawString(100, y, signature[i:i + chars_per_line])
            y -= 10
    
    # QR Code
    if qr_path:
        c.drawImage(qr_path, 400, 400, width=150, height=150)
    
    c.save()
    
    return output_path