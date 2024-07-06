import streamlit as st
from PIL import Image
import base64
import requests
from g4f.client import Client
from utils.helper import save_as_pdf, save_as_doc, save_as_txt
from utils.ocr import image_to_text
import pyperclip
import io
import sqlite3


def init_db():
    conn = sqlite3.connect('notes.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY, content TEXT)''')
    conn.commit()
    return conn, c


def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def process_images(uploaded_files):
    text_list = []
    for uploaded_file in uploaded_files:
        image = Image.open(uploaded_file)
        if image.mode == 'RGBA':
            image = image.convert('RGB')
        st.image(image, caption='Uploaded Image', use_column_width=True)
        extracted_text = image_to_text(image)
        text_list.append(extracted_text)
        st.success('Processed Image Successfully!')
    return text_list


def generate_prompt(combined_text):
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
    return prompt


def get_bot_response(prompt):
    client = Client()
    response = client.chat.completions.create(
        model='gpt-4o',
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content


def display_saved_notes(c):
    st.sidebar.title("Saved Notes")
    c.execute("SELECT id, content FROM notes")
    rows = c.fetchall()
    for row in rows:
        note_id, note_content = row
        if st.sidebar.button(" ".join(note_content.split()[0:15]), key=note_id):
            st.write(note_content)


def main():
    load_css("style.css")
    conn, c = init_db()
    st.logo('logoo.png')
    st.title("📝 Turn your photos into notes with AI")
    uploaded_files = st.file_uploader("📁 Choose images...", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

    if uploaded_files:
        text_list = process_images(uploaded_files)
        combined_text = "\n\n".join(text_list)
        prompt = generate_prompt(combined_text)
        bot_response = get_bot_response(prompt)
        st.subheader("Generated Notes")
        st.write(bot_response)
        st.markdown('---')
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.download_button('Save as TXT', save_as_txt(bot_response), file_name='notes.txt')
        with col2:
            st.download_button('Save as PDF', data=save_as_pdf(bot_response), file_name='notes.pdf')
        with col3:
            st.download_button('Save as DOCX', save_as_doc(bot_response), file_name='notes.docx')
        with col4:
            if st.button('Copy to Clipboard'):
                pyperclip.copy(bot_response)
                st.success("Content copied to clipboard!")

        c.execute("INSERT INTO notes (content) VALUES (?)", (bot_response,))
        conn.commit()
        st.success('Notes saved in App.')

        st.markdown('---')

    display_saved_notes(c)
    conn.close()


if __name__ == "__main__":
    main()
