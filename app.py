import streamlit as st
from PIL import Image
import pytesseract
import requests
from g4f.client import Client
from fpdf import FPDF
from docx import Document
import io
import os

st.title("Image to Text, Trend Analysis, and Note Generation")

uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# to the main of page in the app itself we need to create a

def save_as_txt(content):
    return io.StringIO(content)


def save_as_pdf(content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, content)
    buffer = io.BytesIO()
    pdf.output(buffer)
    return buffer.getvalue()


def save_as_doc(content):
    doc = Document()
    doc.add_paragraph(content)
    buffer = io.BytesIO()
    doc.save(buffer)
    return buffer.getvalue()

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption='Uploaded Image.', use_column_width=True)

    text = pytesseract.image_to_string(image)
    st.write("Extracted Text:")
    st.write(text)

    prompt = f"""
    You are an expert note-taker. Your task is to extract and organize the most critical information from the uploaded images.
    These images often come from slides, meeting notes, or similar sources.

    Your notes should be:
    - **Concise**: Focus on the key points.
    - **Clear**: Easy to understand and follow.
    - **Well-structured**: Formatted for readability.

    Avoid adding unnecessary commentary. Structure your notes as follows:

    ## Title
    - **Summary**: A brief paragraph summarizing the main points.
    - **Details**: Organized information from the image, using bullet points or numbered lists where applicable.
    - **Tables**: Retain the original table format, ensuring all data is accurately captured.

    Maintain the language used in the image. Do not translate or alter the text.

    Here is the extracted text:

    {text}
    """

    client = Client()
    response = client.chat.completions.create(
        model='gpt-4o',
        messages=[{"role": "user", "content": prompt}],
    )
    bot_response = response.choices[0].message.content

    st.write(bot_response)

    option = st.selectbox('Select download format', ('.txt', '.pdf', '.doc'))

    if option == '.txt':
        st.download_button('Download Notes', save_as_txt(bot_response), file_name='notes.txt')
    elif option == '.pdf':
        st.download_button('Download Notes', save_as_pdf(bot_response), file_name='notes.pdf')
    elif option == '.doc':
        st.download_button('Download Notes', save_as_doc(bot_response), file_name='notes.docx')

    # Notion Integration
    def create_notion_page(token, database_id, title, content):
        url = 'https://api.notion.com/v1/pages'
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Notion-Version": "2021-08-16"
        }
        data = {
            "parent": {"database_id": database_id},
            "properties": {
                "Name": {"title": [{"text": {"content": title}}]}
            },
            "children": [{
                "object": "block",
                "type": "paragraph",
                "paragraph": {"text": [{"type": "text", "text": {"content": content}}]}
            }]
        }
        response = requests.post(url, headers=headers, json=data)
        return response.json()

    notion_token = os.getenv('NOTION_TOKEN')
    notion_database_id = os.getenv('NOTION_DATABASE_ID')
    notion_response = create_notion_page(notion_token, notion_database_id, "Generated Notes", bot_response)
    st.write("Notes saved to Notion")


