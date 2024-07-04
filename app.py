import streamlit as st
from PIL import Image
import pytesseract
import requests
from g4f.client import Client
from fpdf import FPDF
from docx import Document
import io
import pyperclip

st.set_page_config(page_title="Enhanced Note Generator", layout="wide")

st.title("📝 Image to Text, Trend Analysis, and Note Generation")

uploaded_file = st.file_uploader("📁 Choose an image...", type=["jpg", "jpeg", "png"])

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


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


if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption='Uploaded Image', use_column_width=True)

    text = pytesseract.image_to_string(image)
    st.markdown('---')

    prompt = f"""
    You are an expert note-taker. Extract and organize the critical information from the uploaded image.
    The notes should be:
    - **long**: The notes should have a minimum length of 200 and a maximum length of 1000 to 20000 characters.
    - **Concise**: Focus on key points.
    - **Clear**: Easy to read.
    - **Well-structured**: Organized format.

    Avoid unnecessary commentary. Structure notes as follows:

    ## Title
    - **Intro**: Description of the image.
    - **Details**: Bullet points or lists.
    - **Summary**: Brief paragraph summarizing main points.
    - **Source**: Provide some link or reference about the image.

    Maintain the original language from the image. Do not alter the text.

    Extracted text:

    {text}
    """

    client = Client()
    response = client.chat.completions.create(
        model='gpt-4o',
        messages=[{"role": "user", "content": prompt}],
    )
    bot_response = response.choices[0].message.content

    st.subheader("Generated Notes")
    st.write(bot_response)

    st.markdown('---')

    col1, col2, col3 = st.columns([2, 1, 1])
    option = st.selectbox('Select download format', ('.txt', '.pdf', '.doc'))

    with col1:

        if option == '.txt':
            st.download_button('Download Notes', save_as_txt(bot_response), file_name='notes.txt')
        elif option == '.pdf':
            st.download_button('Download Notes', save_as_pdf(bot_response), file_name='notes.pdf')
        elif option == '.doc':
            st.download_button('Download Notes', save_as_doc(bot_response), file_name='notes.docx')

    with col2:
        if st.button('Copy to Clipboard'):
            pyperclip.copy(bot_response)
            st.success("Content copied to clipboard!")

