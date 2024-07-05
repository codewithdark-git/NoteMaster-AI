from fpdf import FPDF
from docx import Document
import io


def save_as_txt(content):
    buffer = io.BytesIO()
    buffer.write(content.encode())
    buffer.seek(0)
    return buffer


def save_as_pdf(content):
    buffer = io.BytesIO()
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, content)
    pdf.output(buffer)
    buffer.seek(0)
    return buffer


def save_as_doc(content):
    doc = Document()
    doc.add_paragraph(content)
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

