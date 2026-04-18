# PDF Transcriber

OCR-based transcription tool for scanned PDF documents, optimized for high-quality scans (300 dpi) with structured content (e.g., IRS forms, tax documents).

## Features

- **Tesseract OCR** — battle-tested for structured, monospaced printed text
- **Intelligent rotation detection** — Hough line detection (coarse) + Tesseract confidence refinement (fine)
- **Layout-preserving output** — groups words into proper lines, preserves indentation
- **Batch processing** — handles multi-page PDFs with page breaks
- **Automatic rotation correction** — detects and corrects tilted pages via binary search

## Requirements

- Python 3.11+
- System: `tesseract-ocr` and `poppler-utils`

## Installation

```bash
sudo apt install tesseract-ocr poppler-utils
cd pdf-transcriber && source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

```bash
# Transcribe to stdout
python3 main.py document.pdf

# Transcribe and save
python3 main.py document.pdf -o transcript.txt
```

## Output Format

Plain text with preserved layout. Words on the same baseline are grouped into lines. Indentation reflects horizontal position. Pages separated by `================`.

## Experiments

### OCR Engine Selection

**Tried**: PaddleOCR, EasyOCR, Tesseract

- **PaddleOCR**: Modern deep learning, but struggled with monospaced forms and had CUDA 13.2/RTX 5070 compatibility issues (oneDNN instruction errors)
- **EasyOCR**: PyTorch-based, good CUDA support, but produces word-level detections that are hard to reassemble into proper lines. Output was vertical word-by-word instead of horizontal lines
- **Tesseract** (v4+): Uses LSTM neural networks. Designed for structured printed text. Dramatically better at monospaced forms. Returns proper line-level data via `image_to_data()`. Clear winner for this use case

**Lesson**: Different OCR architectures are optimized for different tasks. Tesseract v4's LSTM approach excels at structured printed text with clear baselines; EasyOCR trades per-word confidence for flexibility on messy/varied layouts. For clean IRS forms, Tesseract's specialization outperformed the more general-purpose models.

### Rotation Detection

**Tried**: Pure Hough line detection (aggressive), coarse-to-fine Hough, Hough + Tesseract binary search

- **Pure Hough (201 angles)**: Slow, and the "count of horizontal lines" metric doesn't correlate with OCR quality. Actually made output worse by picking wrong angles
- **Coarse-to-fine Hough (1° then 0.1°)**: Faster, but still optimizes for edge geometry, not text readability
- **Hough (coarse 1°) + Tesseract (binary search)**: **Winner**. Uses Hough for speed to find ballpark (-10 to +10°, 21 tests), then binary-searches around it using actual Tesseract confidence. Converges in ~10 Tesseract runs instead of 200+. Accurate and acceptably fast

**Lesson**: Optimize for the right metric. Raw geometric features (line counts) are a poor proxy for OCR quality. Direct measurement (Tesseract confidence) is slower but worth it.
