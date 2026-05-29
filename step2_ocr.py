"""
Step 2: OCR code from screenshots, group by file name.
Usage:
  python step2_ocr.py -i ./screenshots -o ./ocr_output
  python step2_ocr.py -i ./screenshots -o ./ocr_output --tesseract "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
"""

import os
import re
import sys
import argparse

import cv2
import numpy as np
import pytesseract


def find_tesseract(custom_path=None):
    """Find the Tesseract executable."""
    if custom_path:
        if os.path.exists(custom_path):
            return custom_path
        print(f"[WARN] Tesseract not found at: {custom_path}")

    # Common install locations
    candidates = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        r"C:\Users\{}\AppData\Local\Programs\Tesseract-OCR\tesseract.exe".format(
            os.environ.get("USERNAME", "")
        ),
        "tesseract",  # on PATH (Linux/Mac)
    ]
    for path in candidates:
        if os.path.exists(path):
            return path

    print("[WARN] Tesseract not found automatically. Trying 'tesseract' on PATH.")
    return "tesseract"


def crop_code_area(gray):
    """Crop out menu bar and side UI, keep code area only."""
    h, w = gray.shape
    return gray[int(h * 0.10):int(h * 0.95), int(w * 0.03):int(w * 0.97)]


def preprocess(img):
    """Upscale + OTSU binarization for better OCR accuracy."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cropped = crop_code_area(gray)
    h, w = cropped.shape
    scaled = cv2.resize(cropped, (w * 2, h * 2), interpolation=cv2.INTER_CUBIC)
    _, thresh = cv2.threshold(scaled, 150, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    return thresh


def ocr_image(img):
    """OCR a single image, return raw text."""
    thresh = preprocess(img)
    config = r'--oem 3 --psm 6'
    return pytesseract.image_to_string(thresh, lang='eng', config=config)


def is_code_line(line):
    """Check if a line looks like code (not UI element)."""
    stripped = line.strip()
    if not stripped:
        return False
    ui_short = {'File', 'Edit', 'View', 'Navigate', 'Code', 'Terminal',
                'Run', 'Help', 'Window', 'Tools', 'Debug', 'Build'}
    if stripped in ui_short:
        return False
    if not any(c in line for c in '=(){};<>[]+-/*.:\'"_'):
        if not stripped[0].isupper() and stripped not in ('return', 'break', 'continue', 'pass', 'import'):
            return False
    return True


def fix_ocr_artifacts(line):
    """Fix common OCR mistakes."""
    fixes = [
        (r'\bImp1\b', 'Impl'), (r'\bpub1ic\b', 'public'), (r'\bvo1d\b', 'void'),
        (r'\bprivale\b', 'private'), (r'\bprolected\b', 'protected'),
        (r'\bclags\b', 'class'), (r'\bStr1ng\b', 'String'),
        (r'\bPacKage\b', 'package'), (r'\bimpord\b', 'import'),
        (r'\bextemds\b', 'extends'), (r'\bimplements\b', 'implements'),
        ('，', ','), ('；', ';'), ('：', ':'),
        ('（', '('), ('）', ')'),
        ('“', '"'), ('”', '"'), ('‘', "'"), ('’', "'"),
        ('【', '['), ('】', ']'),
    ]
    for pat, repl in fixes:
        line = re.sub(pat, repl, line)
    return line


def detect_filename(text_block):
    """Try to detect the file name from the code content."""
    m = re.search(r'public\s+class\s+(\w+)', text_block)
    if m:
        return m.group(1) + '.java'
    m = re.search(r'class\s+(\w+)', text_block)
    if m and m.group(1)[0].isupper():
        return m.group(1) + '.java'
    m = re.search(r'class\s+(\w+)[\(:]', text_block)
    if m:
        return m.group(1).lower() + '.py'
    m = re.search(r'(?://|#|/\*)\s*(\w+\.(java|py|cpp|ts|js|go|rs))', text_block)
    if m:
        return m.group(1)
    return None


def extract_code_blocks(raw_text):
    """Extract code lines from raw OCR text."""
    lines = raw_text.split('\n')
    code_lines = []
    for line in lines:
        line = line.rstrip()
        if is_code_line(line):
            line = fix_ocr_artifacts(line)
            code_lines.append(line)
    return code_lines


def group_into_files(all_code_lines):
    """Group code lines into files by detecting class/package boundaries."""
    files = {}
    current_name = None

    combined = '\n'.join(all_code_lines)
    segments = re.split(
        r'\n(?=(?:package\s|import\s|#include\s|'
        r'public\s+class\s|public\s+interface\s|'
        r'class\s+[A-Z]\w+|'
        r'@\w+\n(?:public\s+)?class))',
        combined
    )

    for seg in segments:
        seg = seg.strip()
        if len(seg) < 20:
            continue
        name = detect_filename(seg)
        if name:
            if name not in files:
                files[name] = []
            files[name].append(seg)
            current_name = name
        elif current_name:
            files[current_name].append(seg)
        else:
            if '_unsorted' not in files:
                files['_unsorted'] = []
            files['_unsorted'].append(seg)

    return files


def main():
    parser = argparse.ArgumentParser(
        description="OCR code from screenshots, grouped by detected file name"
    )
    parser.add_argument("-i", required=True, help="Directory containing PNG screenshots")
    parser.add_argument("-o", default="./ocr_output", help="Output directory for txt files")
    parser.add_argument("--tesseract", default=None, help="Path to tesseract.exe")
    args = parser.parse_args()

    if not os.path.isdir(args.i):
        print(f"[FAIL] Input directory not found: {args.i}")
        sys.exit(1)

    tesseract_path = find_tesseract(args.tesseract)
    pytesseract.pytesseract.tesseract_cmd = tesseract_path
    print(f"[OK] Tesseract: {tesseract_path}")

    os.makedirs(args.o, exist_ok=True)

    shots = sorted(f for f in os.listdir(args.i) if f.lower().endswith('.png'))
    if not shots:
        print(f"[FAIL] No PNG files found in: {args.i}")
        sys.exit(1)

    print(f"[OK] Found {len(shots)} screenshots")

    all_code = []
    for fname in shots:
        path = os.path.join(args.i, fname)
        img = cv2.imread(path)
        if img is None:
            continue
        raw = ocr_image(img)
        lines = extract_code_blocks(raw)
        if lines:
            print(f"  {fname}: {len(lines)} code lines")
            all_code.extend(lines)
        else:
            print(f"  {fname}: (no code detected)")

    if not all_code:
        print("[DONE] No code detected in any screenshot.")
        return

    files = group_into_files(all_code)

    print(f"\n[OK] Detected {len(files)} files:")
    for fname, blocks in files.items():
        safe_name = fname.replace('.', '_') + '.txt'
        out_path = os.path.join(args.o, safe_name)
        content = '\n\n'.join(blocks)
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  {fname} -> {out_path} ({len(content.splitlines())} lines)")

    print(f"\n[DONE] Output: {args.o}")


if __name__ == "__main__":
    main()
