import streamlit as st
from PIL import Image
import pytesseract
# from transformers import pipeline/
import requests
from g4f.client import Client
# import easyocr

st.title("Image to Text, Trend Analysis, and Note Generation")

# Image Upload when image upload then perform all task on it
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption='Uploaded Image.', use_column_width=True)


    # def extract_text_from_image(image_path, lang=['en']):
    #     # Initialize the OCR reader
    #     reader = easyocr.Reader(lang)  # 'en' for English, you can add more languages if needed
    #
    #     # Read the image
    #     result = reader.readtext(image_path)
    #
    #     # Extract and combine the text
    #     extracted_text = " ".join([text[1] for text in result])
    #
    #     return extracted_text
    #
    # Image to Text
    text = pytesseract.image_to_string(image)
    st.write("Extracted Text:")
    st.write(text)

    # # Topic Analysis
    # classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
    # topics = ["technology", "science", "art", "history", "business"]
    # classification = classifier(text, topics)
    # st.write("Identified Topics:")
    # st.write(classification)

    # # Text Generation
    # generator = pipeline("text-generation", model="gpt-2")
    # st.write("Generated Article:")
    # article = generator(f"Write an article about {classification['labels'][0]} based on the following text: {text}",
    #                     max_length=300)
    # st.write(article[0]['generated_text'])

    prompt = f"""
        You are a diligent note-taker. For the uploaded images, generate notes containing the most important information.
        These images are typically taken from slides, meeting notes, or similar sources. Your task is to help extract and structure the notes.
        
        Provide the output directly in the format of notes, without any additional commentary. The generated notes should be structured as follows:
        
        ## Title
        - A summary paragraph.
        - Detailed information extracted from the image.
        - Any tables should retain their original format.
        
        Use the same language as the text in the image. Do not change the language.
        
        {text}
    """


    client = Client()
    response = client.chat.completions.create(
        model='gpt-4o',
        messages=[{"role": "user", "content": prompt}],
    )
    bot_response = response.choices[0].message.content

    st.write(bot_response)

    #
    # # Notion Integration
    # def create_notion_page(token, database_id, title, content):
    #     url = 'https://api.notion.com/v1/pages'
    #     headers = {
    #         "Authorization": f"Bearer {token}",
    #         "Content-Type": "application/json",
    #         "Notion-Version": "2021-08-16"
    #     }
    #     data = {
    #         "parent": {"database_id": database_id},
    #         "properties": {
    #             "Name": {"title": [{"text": {"content": title}}]}
    #         },
    #         "children": [{
    #             "object": "block",
    #             "type": "paragraph",
    #             "paragraph": {"text": [{"type": "text", "text": {"content": content}}]}
    #         }]
    #     }
    #     response = requests.post(url, headers=headers, json=data)
    #     return response.json()
    #
    # notion_token = "YOUR_NOTION_TOKEN"
    # notion_database_id = "YOUR_NOTION_DATABASE_ID"
    # notion_response = create_notion_page(notion_token, notion_database_id, "Generated Article",
    #                                      article[0]['generated_text'])
    # st.write("Article saved to Notion")

# import pytesseract
# print(pytesseract.get_tesseract_version())

