import hashlib
import io
import os
from pathlib import Path

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import qrcode

from database import init_db, insert_record, get_record_by_hash, get_record_by_id, update_filepath
from rsa_signer import generate_keypair, sign_hash, verify_signature
from pdf_generator import generate_pdf
from diff_visualizer import compare_text, compare_images
from tamper_report import generate_tamper_report

UPLOAD_DIR = Path(__file__).resolve().parent / "uploads"
CERT_DIR = Path(__file__).resolve().parent / "certificates"
DIFF_DIR = Path(__file__).resolve().parent / "diffs"
QR_DIR = Path(__file__).resolve().parent / "qr"
UPLOAD_DIR.mkdir(exist_ok=True)
CERT_DIR.mkdir(exist_ok=True)
DIFF_DIR.mkdir(exist_ok=True)
QR_DIR.mkdir(exist_ok=True)

TEXT_EXTENSIONS = {".txt"}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg"}


def _next_cert_path(record_id: int) -> Path:
    """Return the next available certificate path for a given record ID.

    First call  -> certificates/certificate-26.pdf
    Second call -> certificates/certificate-26(1).pdf
    Third call  -> certificates/certificate-26(2).pdf  …and so on.
    """
    base = CERT_DIR / f"certificate-{record_id}.pdf"
    if not base.exists():
        return base
    counter = 1
    while True:
        candidate = CERT_DIR / f"certificate-{record_id}({counter}).pdf"
        if not candidate.exists():
            return candidate
        counter += 1


def _next_diff_path(record_id: int) -> Path:
    """Return the next available diff image path for a given record ID.

    First call  -> diffs/diff-26.png
    Second call -> diffs/diff-26(1).png
    Third call  -> diffs/diff-26(2).png  …and so on.
    """
    base = DIFF_DIR / f"diff-{record_id}.png"
    if not base.exists():
        return base
    counter = 1
    while True:
        candidate = DIFF_DIR / f"diff-{record_id}({counter}).png"
        if not candidate.exists():
            return candidate
        counter += 1


app = FastAPI()
init_db()
generate_keypair()

def compute_hash(file):
    sha256 = hashlib.sha256()
    while chunk := file.read(8192):
        sha256.update(chunk)
    file.seek(0)
    return sha256.hexdigest()

@app.get("/")
def home():
    return {"message": "EvidenceChain backend running"}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    file_like = io.BytesIO(contents)

    hash_val = compute_hash(file_like)
    signature = sign_hash(hash_val)

    # Insert record first to get record_id
    record_id = insert_record(file.filename, hash_val, signature)

    # Save original file as uploads/{record_id}_{original_filename}
    saved_name = f"{record_id}_{file.filename}"
    saved_path = str(UPLOAD_DIR / saved_name)
    with open(saved_path, "wb") as f:
        f.write(contents)

    # Update DB with file path
    update_filepath(record_id, saved_path)

    qr_data = f"http://10.1.59.39:8000/verify-page?id={record_id}"
    qr = qrcode.make(qr_data)
    qr_path = str(QR_DIR / f"qr_{record_id}.png")
    qr.save(qr_path)
    pdf_path = str(_next_cert_path(record_id))
    generate_pdf(file.filename, hash_val, qr_path, signature=signature, output_path=pdf_path)

    return {
        "filename": file.filename,
        "sha256": hash_val,
        "qr_code": qr_path,
        "verify_url": qr_data,
        "record_id": record_id,
        "pdf": pdf_path,
        "signature": signature
    }

@app.post("/verify")
async def verify_file(id: int, file: UploadFile = File(...)):
    try:
        contents = await file.read()

        sha256 = hashlib.sha256()
        sha256.update(contents)
        hash_val = sha256.hexdigest()

        record = get_record_by_id(id)

        if not record:
            return HTMLResponse("<h1>Invalid Record</h1>")

        stored_hash = record[2]
        stored_signature = record[4]   # index 3 is timestamp, 4 is signature
        original_path = record[5]      # index 5 is filepath

        is_valid = (
            hash_val == stored_hash and
            verify_signature(stored_hash, stored_signature)
        )

        # AUTHENTIC
        if is_valid:
            short_hash = stored_hash[:16] + "..." + stored_hash[-16:]
            timestamp = record[3]
            return HTMLResponse(f"""
            <html>
            <head>
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Verification — Authentic</title>
                <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
            </head>
            <body style="margin:0; padding:0; background:#0b1220; font-family:'Inter',system-ui,sans-serif;
                         min-height:100vh; display:flex; align-items:center; justify-content:center;">
                <div style="padding:48px 24px; max-width:480px; width:100%;">

                    <p style="color:#6b7280; font-size:10px; font-weight:600; letter-spacing:3px;
                              text-transform:uppercase; margin:0 0 12px 0; text-align:center;">Verification Status</p>

                    <h1 style="color:#4ade80; font-size:clamp(32px,7vw,44px); margin:0 0 8px 0;
                               font-weight:800; letter-spacing:-1px; text-align:center;">AUTHENTIC</h1>

                    <p style="color:#9ca3af; font-size:14px; margin:0 0 36px 0; text-align:center;
                              line-height:1.5;">This file matches the certified original</p>

                    <div style="border-top:1px solid #1f2937; margin-bottom:32px;"></div>

                    <div style="background:#111827; border:1px solid #1f2937; border-radius:14px;
                                padding:28px 24px;">

                        <div style="margin-bottom:20px;">
                            <p style="color:#6b7280; font-size:10px; font-weight:600; letter-spacing:2px;
                                      text-transform:uppercase; margin:0 0 6px 0;">Filename</p>
                            <p style="color:#e5e7eb; font-size:14px; margin:0; word-break:break-all;">{record[1]}</p>
                        </div>

                        <div style="margin-bottom:20px;">
                            <p style="color:#6b7280; font-size:10px; font-weight:600; letter-spacing:2px;
                                      text-transform:uppercase; margin:0 0 6px 0;">Timestamp</p>
                            <p style="color:#e5e7eb; font-size:14px; margin:0;">{timestamp}</p>
                        </div>

                        <div style="margin-bottom:20px;">
                            <p style="color:#6b7280; font-size:10px; font-weight:600; letter-spacing:2px;
                                      text-transform:uppercase; margin:0 0 6px 0;">SHA-256 Hash</p>
                            <p style="color:#9ca3af; font-size:12px; margin:0; font-family:'Courier New',monospace;
                                      word-break:break-all; line-height:1.6;">{short_hash}</p>
                        </div>

                        <div style="border-top:1px solid #1f2937; padding-top:20px;
                                    display:flex; align-items:center; justify-content:space-between;">
                            <p style="color:#6b7280; font-size:10px; font-weight:600; letter-spacing:2px;
                                      text-transform:uppercase; margin:0;">Digital Signature</p>
                            <span style="background:rgba(74,222,128,0.1); color:#4ade80; padding:5px 16px;
                                        border-radius:6px; font-size:11px; font-weight:700;
                                        letter-spacing:1px;">VALID</span>
                        </div>
                    </div>

                    <p style="color:#374151; font-size:10px; margin-top:36px; text-align:center;
                              letter-spacing:1px;">EvidenceChain &middot; Cryptographic Verification System</p>
                </div>
            </body>
            </html>
            """)

        # TAMPERED — save temp file for diff
        temp_path = f"temp_{file.filename}"
        with open(temp_path, "wb") as f:
            f.write(contents)

        file_ext = file.filename.lower()

        # TEXT
        if file_ext.endswith(".txt"):
            with open(original_path, "rb") as f1, open(temp_path, "rb") as f2:
                diff_result = compare_text(f1.read(), f2.read())

            # Generate tamper report (no diff image for text files)
            report_path = generate_tamper_report(id, original_path, temp_path, "")
            report_rel = os.path.relpath(report_path, Path(__file__).resolve().parent).replace("\\", "/")

            return HTMLResponse(f"""
            <html>
            <head>
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Verification — Tamper Detected</title>
                <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
            </head>
            <body style="margin:0; padding:0; background:#0b1220; font-family:'Inter',system-ui,sans-serif;
                         min-height:100vh; display:flex; align-items:center; justify-content:center;">
                <div style="padding:48px 24px; max-width:620px; width:100%;">

                    <p style="color:#6b7280; font-size:10px; font-weight:600; letter-spacing:3px;
                              text-transform:uppercase; margin:0 0 12px 0; text-align:center;">Verification Status</p>

                    <h1 style="color:#f87171; font-size:clamp(28px,6vw,40px); margin:0 0 8px 0;
                               font-weight:800; letter-spacing:-0.5px; text-align:center;">TAMPER DETECTED</h1>

                    <p style="color:#9ca3af; font-size:14px; margin:0 0 36px 0; text-align:center;
                              line-height:1.5;">This file differs from the certified original</p>

                    <div style="border-top:1px solid #1f2937; margin-bottom:28px;"></div>

                    <div style="background:#111827; border:1px solid #1f2937; border-radius:14px;
                                padding:20px 24px; margin-bottom:24px;
                                display:flex; align-items:center; justify-content:space-between;">
                        <p style="color:#9ca3af; font-size:13px; margin:0;">Hash mismatch detected</p>
                        <span style="background:rgba(248,113,113,0.1); color:#f87171; padding:5px 16px;
                                    border-radius:6px; font-size:11px; font-weight:700;
                                    letter-spacing:1px; white-space:nowrap;">FAILED</span>
                    </div>

                    <p style="color:#6b7280; font-size:10px; font-weight:600; letter-spacing:2px;
                              text-transform:uppercase; margin:0 0 12px 0;">Text Difference Analysis</p>
                    <pre style="text-align:left; background:#111827; color:#d1d5db;
                                padding:20px; border-radius:10px; max-width:100%; box-sizing:border-box;
                                margin:0 0 28px 0; overflow-x:auto; font-size:12px;
                                border:1px solid #1f2937; line-height:1.7;">{diff_result}</pre>

                    <a href="/{report_rel}" target="_blank"
                       style="display:inline-block; padding:13px 32px;
                              background:#1d4ed8; color:#fff; text-decoration:none;
                              border-radius:8px; font-size:14px; font-weight:600;
                              letter-spacing:0.3px;">Download Tamper Report</a>

                    <p style="color:#374151; font-size:10px; margin-top:36px; text-align:center;
                              letter-spacing:1px;">EvidenceChain &middot; Cryptographic Verification System</p>
                </div>
            </body>
            </html>
            """)

        # IMAGE
        elif file_ext.endswith((".png", ".jpg", ".jpeg")):
            print("RUNNING IMAGE DIFF")
            diff_output = str(_next_diff_path(id))
            result = compare_images(original_path, temp_path, diff_output)

            if result == "completely_different":
                # Generate tamper report even for completely different images
                report_path = generate_tamper_report(id, original_path, temp_path, "")
                report_rel = os.path.relpath(report_path, Path(__file__).resolve().parent).replace("\\", "/")

                return HTMLResponse(f"""
                <html>
                <head>
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Verification — Tamper Detected</title>
                    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
                </head>
                <body style="margin:0; padding:0; background:#0b1220; font-family:'Inter',system-ui,sans-serif;
                             min-height:100vh; display:flex; align-items:center; justify-content:center;">
                    <div style="padding:48px 24px; max-width:480px; width:100%;">

                        <p style="color:#6b7280; font-size:10px; font-weight:600; letter-spacing:3px;
                                  text-transform:uppercase; margin:0 0 12px 0; text-align:center;">Verification Status</p>

                        <h1 style="color:#f87171; font-size:clamp(28px,6vw,40px); margin:0 0 8px 0;
                                   font-weight:800; letter-spacing:-0.5px; text-align:center;">TAMPER DETECTED</h1>

                        <p style="color:#9ca3af; font-size:14px; margin:0 0 36px 0; text-align:center;
                                  line-height:1.5;">This file differs from the certified original</p>

                        <div style="border-top:1px solid #1f2937; margin-bottom:28px;"></div>

                        <div style="background:#111827; border:1px solid #1f2937; border-radius:14px;
                                    padding:24px; margin-bottom:24px;">
                            <p style="color:#f87171; font-size:14px; font-weight:600; margin:0 0 8px 0;">Complete content mismatch</p>
                            <p style="color:#9ca3af; font-size:13px; margin:0; line-height:1.5;">The submitted image bears no resemblance to the certified original file.</p>
                        </div>

                        <a href="/{report_rel}" target="_blank"
                           style="display:inline-block; padding:13px 32px;
                                  background:#1d4ed8; color:#fff; text-decoration:none;
                                  border-radius:8px; font-size:14px; font-weight:600;
                                  letter-spacing:0.3px;">Download Tamper Report</a>

                        <p style="color:#374151; font-size:10px; margin-top:36px; text-align:center;
                                  letter-spacing:1px;">EvidenceChain &middot; Cryptographic Verification System</p>
                    </div>
                </body>
                </html>
                """)

            # Relative paths from project root so static file server can find them
            PROJECT_ROOT = Path(__file__).resolve().parent
            diff_rel = os.path.relpath(result, PROJECT_ROOT).replace("\\", "/")
            orig_rel = os.path.relpath(original_path, PROJECT_ROOT).replace("\\", "/")
            temp_rel = os.path.relpath(temp_path, PROJECT_ROOT).replace("\\", "/")

            # Generate tamper report with diff image
            report_path = generate_tamper_report(id, original_path, temp_path, diff_output)
            report_rel = os.path.relpath(report_path, PROJECT_ROOT).replace("\\", "/")

            return HTMLResponse(f"""
            <html>
            <head>
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Verification — Tamper Detected</title>
                <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
            </head>
            <body style="margin:0; padding:0; background:#0b1220; font-family:'Inter',system-ui,sans-serif;
                         min-height:100vh;">
                <div style="padding:48px 24px; max-width:940px; margin:0 auto;">

                    <p style="color:#6b7280; font-size:10px; font-weight:600; letter-spacing:3px;
                              text-transform:uppercase; margin:0 0 12px 0; text-align:center;">Verification Status</p>

                    <h1 style="color:#f87171; font-size:clamp(28px,6vw,40px); margin:0 0 8px 0;
                               font-weight:800; letter-spacing:-0.5px; text-align:center;">TAMPER DETECTED</h1>

                    <p style="color:#9ca3af; font-size:14px; margin:0 0 16px 0; text-align:center;
                              line-height:1.5;">This file differs from the certified original</p>

                    <div style="text-align:center; margin-bottom:36px;">
                        <div style="background:#111827; border:1px solid #1f2937; border-radius:8px;
                                    padding:12px 24px; display:inline-block;">
                            <p style="color:#9ca3af; font-size:13px; margin:0;">Hash mismatch detected</p>
                        </div>
                    </div>

                    <p style="color:#6b7280; font-size:10px; font-weight:600; letter-spacing:2px;
                              text-transform:uppercase; margin:0 0 16px 0; text-align:center;">Visual Comparison</p>

                    <div style="display:flex; justify-content:center; gap:16px; flex-wrap:wrap;
                                margin:0 auto 36px auto;">
                        <div style="flex:1; min-width:180px; max-width:280px;">
                            <p style="color:#9ca3af; font-size:10px; margin:0 0 8px 0; text-transform:uppercase;
                                      letter-spacing:2px; font-weight:600; text-align:center;">Original</p>
                            <img src="/{orig_rel}" style="width:100%; border:1px solid #1f2937;
                                 border-radius:10px; background:#111827;"/>
                        </div>
                        <div style="flex:1; min-width:180px; max-width:280px;">
                            <p style="color:#9ca3af; font-size:10px; margin:0 0 8px 0; text-transform:uppercase;
                                      letter-spacing:2px; font-weight:600; text-align:center;">Submitted</p>
                            <img src="/{temp_rel}" style="width:100%; border:1px solid #1f2937;
                                 border-radius:10px; background:#111827;"/>
                        </div>
                        <div style="flex:1; min-width:180px; max-width:280px;">
                            <p style="color:#9ca3af; font-size:10px; margin:0 0 8px 0; text-transform:uppercase;
                                      letter-spacing:2px; font-weight:600; text-align:center;">Differences</p>
                            <img src="/{diff_rel}" style="width:100%; border:1px solid #1f2937;
                                 border-radius:10px; background:#111827;"/>
                        </div>
                    </div>

                    <div style="text-align:center;">
                        <a href="/{report_rel}" target="_blank"
                           style="display:inline-block; padding:13px 32px;
                                  background:#1d4ed8; color:#fff; text-decoration:none;
                                  border-radius:8px; font-size:14px; font-weight:600;
                                  letter-spacing:0.3px;">Download Tamper Report</a>
                    </div>

                    <p style="color:#374151; font-size:10px; margin-top:36px; text-align:center;
                              letter-spacing:1px;">EvidenceChain &middot; Cryptographic Verification System</p>
                </div>
            </body>
            </html>
            """)

        # DEFAULT — other file types
        report_path = generate_tamper_report(id, original_path, temp_path, "")
        report_rel = os.path.relpath(report_path, Path(__file__).resolve().parent).replace("\\", "/")

        return HTMLResponse(f"""
        <html>
        <head>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Verification — Tamper Detected</title>
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
        </head>
        <body style="margin:0; padding:0; background:#0b1220; font-family:'Inter',system-ui,sans-serif;
                     min-height:100vh; display:flex; align-items:center; justify-content:center;">
            <div style="padding:48px 24px; max-width:480px; width:100%;">

                <p style="color:#6b7280; font-size:10px; font-weight:600; letter-spacing:3px;
                          text-transform:uppercase; margin:0 0 12px 0; text-align:center;">Verification Status</p>

                <h1 style="color:#f87171; font-size:clamp(28px,6vw,40px); margin:0 0 8px 0;
                           font-weight:800; letter-spacing:-0.5px; text-align:center;">TAMPER DETECTED</h1>

                <p style="color:#9ca3af; font-size:14px; margin:0 0 36px 0; text-align:center;
                          line-height:1.5;">This file differs from the certified original</p>

                <div style="border-top:1px solid #1f2937; margin-bottom:28px;"></div>

                <div style="background:#111827; border:1px solid #1f2937; border-radius:14px;
                            padding:24px; margin-bottom:28px;">
                    <p style="color:#f87171; font-size:14px; font-weight:600; margin:0 0 8px 0;">Integrity check failed</p>
                    <p style="color:#9ca3af; font-size:13px; margin:0; line-height:1.5;">No visual comparison available for this file type. Download the report for a detailed analysis.</p>
                </div>

                <a href="/{report_rel}" target="_blank"
                   style="display:inline-block; padding:13px 32px;
                          background:#1d4ed8; color:#fff; text-decoration:none;
                          border-radius:8px; font-size:14px; font-weight:600;
                          letter-spacing:0.3px;">Download Tamper Report</a>

                <p style="color:#374151; font-size:10px; margin-top:36px; text-align:center;
                          letter-spacing:1px;">EvidenceChain &middot; Cryptographic Verification System</p>
            </div>
        </body>
        </html>
        """)

    except Exception as e:
        print("VERIFY ERROR:", str(e))
        return {"error": str(e)}


@app.get("/verify-id", response_class=HTMLResponse)
def verify_by_id(id: int):
    record = get_record_by_id(id)

    if not record:
        return "<h1>Invalid QR</h1>"

    return f"""
    <html>
        <body style="text-align:center; font-family:sans-serif;">
            <h1 style="color:green;">CERTIFIED FILE</h1>
            <p><b>Filename:</b> {record[1]}</p>
            <p><b>Hash:</b> {record[2]}</p>
            <p><b>Status:</b> ORIGINAL RECORD STORED</p>
        </body>
    </html>
    """

@app.get("/verify-page", response_class=HTMLResponse)
def verify_page(id: int):
    return f"""
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Evidence Verification</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    </head>
    <body style="margin:0; padding:0; background:#0b1220; font-family:'Inter',system-ui,sans-serif;
                 min-height:100vh; display:flex; align-items:center; justify-content:center;">

        <div style="padding:48px 24px; max-width:440px; width:100%;">

            <h1 style="color:#e5e7eb; font-size:clamp(20px,5vw,26px); margin:0 0 8px 0;
                       font-weight:800; letter-spacing:-0.3px; text-align:center;">
                Evidence Verification Portal
            </h1>

            <p style="color:#9ca3af; font-size:13px; margin:0 0 8px 0; text-align:center; line-height:1.5;">
                Upload the file to validate its authenticity against certified records
            </p>

            <p style="color:#4b5563; font-size:11px; margin:0 0 36px 0; text-align:center;">
                This QR was generated at time of certification
            </p>

            <div style="background:#111827; border:1px solid #1f2937; border-radius:16px;
                        padding:32px 28px;">

                <form action="/verify?id={id}" method="post" enctype="multipart/form-data">

                    <div style="text-align:center; margin-bottom:28px;">
                        <span style="background:rgba(59,130,246,0.08); color:#60a5fa; padding:6px 18px;
                                     border-radius:6px; font-size:11px; font-weight:700;
                                     letter-spacing:2px;">RECORD {id}</span>
                    </div>

                    <div style="border:1px dashed #374151; border-radius:12px; padding:28px 20px;
                                margin-bottom:28px; background:rgba(17,24,39,0.5); text-align:center;">

                        <p style="color:#9ca3af; font-size:13px; margin:0 0 16px 0;">
                            Select the evidence file
                        </p>

                        <label style="display:inline-block; padding:10px 28px; background:#1f2937;
                                      color:#d1d5db; border-radius:8px; font-size:13px; font-weight:600;
                                      cursor:pointer; border:1px solid #374151;">
                            <input type="file" name="file" required
                                   style="position:absolute; opacity:0; width:0; height:0;"
                                   onchange="this.parentElement.nextElementSibling.textContent =
                                             this.files[0] ? this.files[0].name : 'No file selected'"/>
                            Choose File
                        </label>

                        <p style="color:#4b5563; font-size:12px; margin:12px 0 0 0;
                                  word-break:break-all;">No file selected</p>
                    </div>

                    <button type="submit"
                            style="width:100%; padding:14px 0; background:#1d4ed8;
                                   color:#fff; border:none; border-radius:10px; font-size:14px;
                                   font-weight:700; cursor:pointer; letter-spacing:0.3px;">
                        Verify Evidence
                    </button>
                </form>
            </div>

            <p style="color:#374151; font-size:10px; margin-top:32px; text-align:center;
                      line-height:1.6; letter-spacing:0.5px;">
                Verification performed using cryptographic hashing and digital signatures
            </p>
        </div>
    </body>
    </html>
    """

# Static file serving — mounted AFTER all routes so it doesn't shadow them
app.mount("/", StaticFiles(directory="."), name="static")
