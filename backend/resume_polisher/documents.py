"""PDF and DOCX text extraction."""

import io
import fitz
from docx import Document
from resume_polisher.config import DOCX_EXTENSION, PDF_EXTENSION


def extension_kind(filename: str) -> str | None:
    """Return 'pdf', 'docx', or None based on the filename suffix (case-insensitive)."""

    # Lowercasing avoids issues like Resume.PDF vs resume.pdf.
    lowered = filename.lower()
    if lowered.endswith(PDF_EXTENSION):
        return "pdf"
    if lowered.endswith(DOCX_EXTENSION):
        return "docx"
    return None


def extract_pdf_text(file_bytes: bytes) -> str:
    """Pull plain text from a PDF byte blob using PyMuPDF."""

    # TODO: understand this — `stream=` parses uploads in memory without writing temp files.
    chunks: list[str] = []
    with fitz.open(stream=file_bytes, filetype="pdf") as document:
        for page in document:
            chunks.append(page.get_text())
    return "\n".join(chunks).strip()


def extract_docx_text(file_bytes: bytes) -> str:
    """Pull plain text from a .docx byte blob using python-docx."""

    # TODO: understand this — Word files are ZIPs; BytesIO lets us read it from memory.
    buffer = io.BytesIO(file_bytes)
    document = Document(buffer)
    return "\n".join(paragraph.text for paragraph in document.paragraphs).strip()


def extract_text_for_kind(kind: str, file_bytes: bytes) -> str:
    """Dispatch to the correct extractor so each format stays isolated and testable."""

    if kind == "pdf":
        return extract_pdf_text(file_bytes)
    return extract_docx_text(file_bytes)
