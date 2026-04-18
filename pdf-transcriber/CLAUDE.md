# pdf-transcriber

OCR tool for high-quality scanned PDFs (IRS documents, 300 dpi). Converts pages to text with layout preservation.

## Privacy & Security

**CRITICAL**: This directory processes sensitive financial documents. 

- **Never commit documents or transcripts**: `data/`, `*.pdf`, `*.txt` are gitignored.
- **Never persist analysis**: Do not write summaries, derived insights, or document details to memory files, plans, or version control.
- **Stateless processing**: Process PDFs in-memory, return output, discard internally. Treat all document content as ephemeral.
- **Pre-commit hooks**: Git operations warn about privacy before push/commit/add.

See `.claude/settings.json` for permission rules and hooks.

## Architecture

- **Input**: PDF files in `data/` (gitignored)
- **Processing**: PaddleOCR with GPU acceleration; auto-rotation correction
- **Output**: Plain-text transcripts with indentation preserved; optionally piped to agents for summarization
- **No intermediate storage**: Results are stdout or direct file writes, never cached

## Running

```bash
source .venv/bin/activate
python main.py data/yourfile.pdf -o data/output.txt
```

First run downloads PaddleOCR models (~100 MB).

## Dependencies

- Python 3.11+
- CUDA 13 + cuDNN (for GPU; CPU fallback available)
- System: `poppler-utils` (for PDF → image)
