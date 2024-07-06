from fpdf import FPDF
from docx import Document
import io
import tempfile


def save_as_txt(content):
    buffer = io.BytesIO()
    buffer.write(content.encode())
    buffer.seek(0)
    return buffer


def save_as_pdf(content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    lines = content.split('\n')
    for line in lines:
        pdf.cell(200, 10, txt=line, ln=True)

    # Save to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        pdf.output(tmp_file.name)
        tmp_file.seek(0)
        pdf_content = tmp_file.read()

    return pdf_content


def save_as_doc(content):
    doc = Document()
    doc.add_paragraph(content)
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer



