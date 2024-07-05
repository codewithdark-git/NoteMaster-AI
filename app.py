import streamlit as st
from PIL import Image
import base64
import requests
from g4f.client import Client
from utils.helper import save_as_pdf, save_as_doc, save_as_txt
from utils.ocr import image_to_text
import pyperclip
import io

st.set_page_config(page_title="Enhanced Note Generator", layout="wide")

st.title("📝 Turn your photos into notes with AI")

uploaded_files = st.file_uploader("📁 Choose images...", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

all_done = 0
text_list = []

if uploaded_files:
    for uploaded_file in uploaded_files:
        image = Image.open(uploaded_file)

        # Convert image to RGB mode if it is in RGBA mode
        if image.mode == 'RGBA':
            image = image.convert('RGB')

        st.image(image, caption='Uploaded Image', use_column_width=True)

        # Convert image to base64
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()

        # Extract text
        extracted_text = image_to_text(image)
        text_list.append(extracted_text)

        all_done += 1
        st.success('Processed Image Successfully!')

    if all_done == len(uploaded_files) and all_done > 0:
        st.balloons()

        combined_text = "\n\n".join(text_list)
        st.markdown('---')

        prompt = f"""
        You are an expert note-taker. Extract and organize the critical information from the uploaded images.
        The notes should be:
        - **long**: The notes should have a minimum length of 200 and a maximum length of 1000 to 20000 characters.
        - **Concise**: Focus on key points.
        - **Clear**: Easy to read.
        - **Well-structured**: Organized format.
        
        Avoid unnecessary commentary. Structure notes as follows:

        ## Title
        - **Intro**: Description of the image.
        - **Details**: solve the problem with more details.
        - **Summary**: Brief paragraph summarizing main points.
        - **Source**: Provide some link or reference about the image.

        If the image contains math-related content: 
        ## Problem Title
        - **Problem Statement**: Clearly state the problem from the image.
        - **Key Concepts**: List and briefly explain any mathematical concepts relevant to the problem.
        - **Step-by-Step Solution**:
          1. [First step]
          2. [Second step]
          3. [Continue with additional steps as needed]
        - **Explanation**: For each step, provide a simple explanation of what's happening and why.
        - **Visual Aid**: If applicable, describe how to draw a diagram or visual representation to help understand the problem.
        - **Final Answer**: Clearly state the solution to the problem.
        - **Real-world Application**: Provide a simple, relatable example of how this math concept is used in everyday life.
        - **Practice Problem**: Suggest a similar, slightly easier problem for the student to try on their own.
        
        Remember:
        - Use the original language from the image.
        - Explain each mathematical symbol or notation used.
        - If multiple methods are possible, mention the simplest one for beginners.
        - Encourage understanding over memorization.

        Extracted text:

        {combined_text}
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

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button('Download as TXT'):
                st.download_button('Download Notes', save_as_txt(bot_response), file_name='notes.txt')

        with col2:
            if st.button('Download as PDF'):
                st.download_button('Download Notes', save_as_pdf(bot_response), file_name='notes.pdf')

        with col3:
            if st.button('Download as DOCX'):
                st.download_button('Download Notes', save_as_doc(bot_response), file_name='notes.docx')

        with col4:
            if st.button('Copy to Clipboard'):
                pyperclip.copy(bot_response)
                st.success("Content copied to clipboard!")

        st.markdown('---')

