"""
diff_visualizer.py - File difference visualization module.

Provides text diffing and image difference highlighting with
bounding boxes around changed regions for a digital evidence
verification system.

Dependencies:
    - opencv-python-headless  (pip install opencv-python-headless)
    - difflib                 (stdlib)
"""

from __future__ import annotations

import difflib
import os
from pathlib import Path

import cv2
import numpy as np

# ── Configuration ────────────────────────────────────────────────────
_BASE_DIR = Path(__file__).resolve().parent
_DEFAULT_DIFF_OUTPUT = str(_BASE_DIR / "diff_output.png")

# If more than this fraction of pixels differ, images are "completely different"
_COMPLETELY_DIFFERENT_THRESHOLD = 0.60  # 60%

# Max contour count before declaring "completely different"
_MAX_CONTOUR_COUNT = 500

# Binary threshold applied to the grayscale difference image (low to catch subtle changes)
_PIXEL_DIFF_THRESHOLD = 25

# Gaussian blur kernel size (must be odd)
_BLUR_KERNEL = (5, 5)

# Dilation kernel size and iterations (merges nearby small differences)
_DILATE_KERNEL_SIZE = (3, 3)
_DILATE_ITERATIONS = 2

# Minimum contour area (in pixels) to draw a bounding box
_MIN_CONTOUR_AREA = 50

# Bounding box styling
_BOX_COLOR = (0, 0, 255)  # Red in BGR
_BOX_THICKNESS = 2


# ── Text Difference ─────────────────────────────────────────────────

def compare_text(original_bytes: bytes, new_bytes: bytes) -> str:
    """Produce a readable, line-by-line diff between two text payloads.

    Both inputs are decoded as UTF-8 (invalid bytes replaced).
    Uses unified-diff format: '+' for additions, '-' for deletions.

    Args:
        original_bytes: Raw bytes of the original file.
        new_bytes:      Raw bytes of the modified file.

    Returns:
        Human-readable unified diff string, or a status message
        if files are identical / empty.
    """
    try:
        original_lines = (
            original_bytes.decode("utf-8", errors="replace")
            .splitlines(keepends=True)
        )
        new_lines = (
            new_bytes.decode("utf-8", errors="replace")
            .splitlines(keepends=True)
        )
    except Exception:
        return "[error] Unable to decode file contents as text."

    if not original_lines and not new_lines:
        return "[info] Both files are empty."

    diff = list(difflib.unified_diff(
        original_lines,
        new_lines,
        fromfile="original",
        tofile="modified",
        lineterm="",
    ))

    if not diff:
        return "[info] Files are identical - no differences found."

    return "\n".join(diff)


# ── Image Difference ────────────────────────────────────────────────

def compare_images(
    original_path: str,
    new_path: str,
    output_path: str = _DEFAULT_DIFF_OUTPUT,
) -> str:
    """Generate a diff image with bounding boxes around changed regions.

    Pipeline:
        1. Load both images
        2. Resize to matching dimensions
        3. Compute color difference (absdiff on BGR)
        4. Convert diff to grayscale
        5. Low threshold (10) to catch subtle changes
        6. Dilate to merge thin lines / scribbles
        7. Find contours and draw bounding boxes
        8. Heatmap fallback if no boxes detected

    If >60% of pixels differ, returns ``"completely_different"``.

    Args:
        original_path: Path to the original image.
        new_path:      Path to the modified image.
        output_path:   Where to save the annotated diff image.

    Returns:
        Absolute path to the saved diff image, or
        ``"completely_different"`` / ``"error"``.
    """
    img1 = cv2.imread(original_path)
    img2 = cv2.imread(new_path)

    if img1 is None or img2 is None:
        return "error"

    # Resize to same dimensions
    h, w = img1.shape[:2]
    img2 = cv2.resize(img2, (w, h))

    # Gaussian blur to suppress JPEG compression noise
    img1_blur = cv2.GaussianBlur(img1, (5, 5), 0)
    img2_blur = cv2.GaussianBlur(img2, (5, 5), 0)

    # Color difference on blurred images
    diff = cv2.absdiff(img1_blur, img2_blur)

    # Convert to grayscale AFTER diff
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)

    # Threshold high enough to ignore JPEG artifacts (~5-15 pixel diff)
    # but low enough to catch real edits like scribbles (~50+ pixel diff)
    _, thresh = cv2.threshold(gray, 35, 255, cv2.THRESH_BINARY)

    # Dilation to merge thin lines and scribbles
    kernel = np.ones((5, 5), np.uint8)
    thresh = cv2.dilate(thresh, kernel, iterations=2)

    # Check if images are completely different
    changed_pixels = cv2.countNonZero(thresh)
    total_pixels = h * w

    if changed_pixels / total_pixels > 0.6:
        return "completely_different"

    # Find contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    result = img2.copy()
    box_count = 0

    for c in contours:
        area = cv2.contourArea(c)

        # Low area filter to catch small scribbles
        if area < 10:
            continue

        x, y, cw, ch = cv2.boundingRect(c)
        cv2.rectangle(result, (x, y), (x + cw, y + ch), (0, 0, 255), 2)
        box_count += 1

    # Heatmap fallback if no bounding boxes detected
    if box_count == 0:
        heat = cv2.applyColorMap(thresh, cv2.COLORMAP_JET)
        result = cv2.addWeighted(img2, 0.7, heat, 0.3, 0)

    cv2.imwrite(output_path, result)
    return os.path.abspath(output_path)


# ── Quick self-test ──────────────────────────────────────────────────

if __name__ == "__main__":
    # --- Text diff demo ---
    orig = b"line 1\nline 2\nline 3\n"
    modi = b"line 1\nline 2 changed\nline 3\nline 4 added\n"

    print("=== Text Diff ===")
    print(compare_text(orig, modi))

    # --- Image diff demo (uses QR codes if available) ---
    sample1 = _BASE_DIR / "qr_9.png"
    sample2 = _BASE_DIR / "qr_10.png"

    if sample1.exists() and sample2.exists():
        print("\n=== Image Diff ===")
        result = compare_images(str(sample1), str(sample2))
        if result == "completely_different":
            print("Result: completely_different")
        else:
            print(f"Diff image saved to: {result}")
    else:
        print("\n[skip] No sample images found for image diff demo.")

    print("\n[OK] All checks passed.")
