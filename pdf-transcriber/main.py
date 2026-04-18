#!/usr/bin/env python3
import sys
import argparse
from pathlib import Path
import cv2
import numpy as np
from pdf2image import convert_from_path
import pytesseract
from PIL import Image
import io


def detect_rotation_angle(image_cv2: np.ndarray) -> float:
    """Detect rotation: Hough coarse (1°), Tesseract binary search refinement."""
    gray = cv2.cvtColor(image_cv2, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    center = (w // 2, h // 2)

    def hough_score(angle):
        matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(gray, matrix, (w, h), borderMode=cv2.BORDER_REPLICATE)
        edges = cv2.Canny(rotated, 50, 150)
        lines = cv2.HoughLines(edges, 1, np.pi / 180, 50)
        if lines is None:
            return 0
        return sum(1 for line in lines if abs(np.degrees(line[0][1])) < 10 or abs(np.degrees(line[0][1]) - 180) < 10)

    def tesseract_score(angle):
        matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(gray, matrix, (w, h), borderMode=cv2.BORDER_REPLICATE)
        pil_img = Image.fromarray(rotated)
        data = pytesseract.image_to_data(pil_img, output_type=pytesseract.Output.DATAFRAME)
        if data.empty or data['conf'].sum() == 0:
            return 0.0
        return data[data['conf'] > 0]['conf'].mean()

    best_angle = 0.0
    best_hough = hough_score(0.0)
    for angle in range(-10, 11):
        score = hough_score(float(angle))
        if score > best_hough:
            best_hough = score
            best_angle = float(angle)

    low, high = best_angle - 1.0, best_angle + 1.0
    while high - low > 0.1:
        mid1 = low + (high - low) / 3.0
        mid2 = high - (high - low) / 3.0
        if tesseract_score(mid1) > tesseract_score(mid2):
            high = mid2
        else:
            low = mid1

    return (low + high) / 2.0


def correct_rotation(pil_image: Image.Image) -> Image.Image:
    """Auto-detect and correct page rotation."""
    image_cv2 = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
    angle = detect_rotation_angle(image_cv2)

    if abs(angle) < 1.0:
        return pil_image

    h, w = image_cv2.shape[:2]
    center = (w // 2, h // 2)
    matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image_cv2, matrix, (w, h), borderMode=cv2.BORDER_REPLICATE)

    return Image.fromarray(cv2.cvtColor(rotated, cv2.COLOR_BGR2RGB))


def transcribe_pdf(pdf_path: str) -> str:
    """Transcribe PDF to plain text with preserved formatting."""
    pdf_file = Path(pdf_path)
    if not pdf_file.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    print(f"Loading PDF: {pdf_file.name}", file=sys.stderr)
    pages = convert_from_path(pdf_path, dpi=300)
    print(f"Loaded {len(pages)} pages", file=sys.stderr)

    all_text = []

    for page_num, page_image in enumerate(pages, 1):
        print(f"Processing page {page_num}/{len(pages)}...", file=sys.stderr)

        corrected = correct_rotation(page_image)

        page_text = extract_text_with_layout(corrected)
        all_text.append(page_text)

        if page_num < len(pages):
            all_text.append("\n" + "=" * 80 + "\n")

    return "".join(all_text)


def extract_text_with_layout(image: Image.Image) -> str:
    """Extract OCR text using Tesseract with layout preservation."""
    data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DATAFRAME)

    if data.empty:
        return ""

    data = data[data['conf'] > 0]
    data = data.sort_values(['top', 'left']).reset_index(drop=True)

    text_lines = []
    current_line_num = None
    current_line = []

    for _, row in data.iterrows():
        line_num = row['line_num']

        if current_line_num is None or line_num == current_line_num:
            current_line.append((row['left'], row['text']))
            current_line_num = line_num
        else:
            if current_line:
                current_line.sort(key=lambda x: x[0])
                x_min = current_line[0][0]
                indent = int(x_min / 50)
                line_text = " ".join(text for _, text in current_line)
                text_lines.append(" " * indent + line_text)
            current_line = [(row['left'], row['text'])]
            current_line_num = line_num

    if current_line:
        current_line.sort(key=lambda x: x[0])
        x_min = current_line[0][0]
        indent = int(x_min / 50)
        line_text = " ".join(text for _, text in current_line)
        text_lines.append(" " * indent + line_text)

    return "\n".join(text_lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Transcribe scanned PDF to plain text using OCR")
    parser.add_argument("pdf_file", help="Path to PDF file")
    parser.add_argument("--output", "-o", help="Output file (default: stdout)", default=None)

    args = parser.parse_args()

    try:
        text = transcribe_pdf(args.pdf_file)

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(text)
            print(f"Transcription saved to: {args.output}", file=sys.stderr)
        else:
            print(text)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
