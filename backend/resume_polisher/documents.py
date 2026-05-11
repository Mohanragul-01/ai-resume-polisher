# documents.py
# This file handles reading text out of uploaded PDF and DOCX files.
# Each file format needs a different library, so we keep them isolated here.
import io
import fitz          # PyMuPDF — used for reading PDF files
from docx import Document   # python-docx — used for reading Word (.docx) files
from resume_polisher.config import DOCX_EXTENSION, PDF_EXTENSION


def extension_kind(filename: str) -> str | None:
    """
    Look at the file extension and return what kind of file it is.

    Returns:
        'pdf'  — if the file ends with .pdf
        'docx' — if the file ends with .docx
        None   — if the file type is not supported
    """

    # Convert to lowercase so Resume.PDF and resume.pdf are treated the same.
    lowered = filename.lower()

    if lowered.endswith(PDF_EXTENSION):
        return "pdf"
    if lowered.endswith(DOCX_EXTENSION):
        return "docx"

    # File type is not supported.
    return None


def extract_pdf_text(file_bytes: bytes) -> str:
    """
    Extract all text from a PDF file.

    `file_bytes` is the raw binary content of the uploaded file.
    We read it directly from memory (no temp files needed).
    """

    # Collect text from each page in a list, then join them at the end.
    page_texts = []

    # fitz.open() with stream= reads the PDF from memory instead of from disk.
    with fitz.open(stream=file_bytes, filetype="pdf") as pdf_document:
        for page in pdf_document:
            page_texts.append(page.get_text())

    # Join all pages with a newline and remove leading/trailing whitespace.
    return "\n".join(page_texts).strip()


def extract_docx_text(file_bytes: bytes) -> str:
    """
    Extract all text from a Word (.docx) file.

    `file_bytes` is the raw binary content of the uploaded file.
    We use BytesIO to read the file from memory (no temp files needed).
    """

    # io.BytesIO wraps the raw bytes so python-docx can read it like a file.
    # Word (.docx) files are actually ZIP archives — python-docx handles that internally.
    buffer = io.BytesIO(file_bytes)
    word_document = Document(buffer)

    # Each paragraph in the Word document becomes one line of text.
    paragraph_texts = [paragraph.text for paragraph in word_document.paragraphs]

    return "\n".join(paragraph_texts).strip()


def extract_text_for_kind(kind: str, file_bytes: bytes) -> str:
    """
    Call the right text extractor based on the file type.

    Args:
        kind       — either 'pdf' or 'docx'
        file_bytes — the raw binary content of the uploaded file

    Returns:
        The extracted plain text from the file.
    """

    if kind == "pdf":
        return extract_pdf_text(file_bytes)

    # If it's not a PDF, it must be a DOCX (we already validated the type earlier).
    return extract_docx_text(file_bytes)
