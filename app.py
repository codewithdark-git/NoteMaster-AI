import streamlit as st
from PIL import Image
import base64
import requests
from g4f.client import Client
import g4f
from g4f.Provider import *
from g4f.Provider import BingCreateImages, OpenaiChat, Gemini
from g4f.models import *
from utils.helper import save_as_pdf, save_as_doc, save_as_txt
from utils.ocr import image_to_text
import sys
import pyperclip
import os
import io
import sqlite3
import datetime

def init_db():
    conn = sqlite3.connect('notes.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS notes (
                 id INTEGER PRIMARY KEY, 
                 content TEXT,
                 timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    return conn, c


def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def process_images(uploaded_files):
    images = []
    text_list = []
    for uploaded_file in uploaded_files:
        image = Image.open(uploaded_file)
        if image.mode == 'RGBA':
            image = image.convert('RGB')
        extracted_text = image_to_text(image)
        text_list.append(extracted_text)
        st.success('Processed Image Successfully!')
        st.balloons()
    return text_list, images


def generate_prompt(combined_text, images, tags):
    prompts = {
        "General": "Create comprehensive notes that summarize the content clearly and concisely.",
        "Coding": "Create detailed notes focusing on coding concepts and examples from the text.",
        "Math": "Create structured notes explaining mathematical concepts and problems from the text.",
        "Student Notes": "Create well-organized notes that highlight important points for students."
    }

    specific_prompts = "\n".join([f"Specific instructions for {tag} images:\n{prompts[tag]}" for tag in tags])

    prompt = f"""
    You are an expert note-taker. For the uploaded {', '.join(tags)} images, generate notes that capture important
    information across various fields. Your task is to extract and organize the key information directly, 
    without unnecessary commentary. Make the notes clear, concise, and well-structured.

    The notes should be:
    - **long**: The notes should have a minimum length of 200 and a maximum length of 1000 to 20000 characters.
    - **Concise**: Focus on key points.
    - **Clear**: Easy to read.
    - **Well-structured**: Organized format.

    {specific_prompts}

    Extracted text:
    {combined_text}

    """
    return prompt


def generate_link_prompt(link, user_prompt):
    prompt = f"""
    This is the user prompt: {user_prompt}. You are an expert note-taker. For the provided {link},
     generate notes that capture important information across various fields. Your task is to extract 
     and organize the key information directly, without unnecessary commentary. Make the notes clear, 
     concise, and well-structured.
    
    The notes should be:
    - **long**: The notes should have a minimum length of 200 and a maximum length of 1000 to 20000 characters.
    - **Concise**: Focus on key points.
    - **Clear**: Easy to read.
    - **Well-structured**: Organized format.
    
    Link:
    {link}
    """
    return prompt


def get_bot_response(prompt):
    client = Client()
    response = client.chat.completions.create(
        model=g4f.models.gpt_35_turbo_16k, #gpt-3.5, blackbox, llama3_70b_instruct, meta, gpt_4o, mixtral_8x7b
        # provider=g4f.Provider.ChatgptAi,
        messages=[{"role": "user", "content": prompt}],
    )

    return response.choices[0].message.content


def display_saved_notes(c, conn):
    st.sidebar.title("Saved Notes")
    c.execute("SELECT id, content FROM notes ORDER BY timestamp DESC")
    rows = c.fetchall()
    for row in rows:
        note_id, note_content = row
        if st.sidebar.button(" ".join(note_content.split()[0:15]), key=note_id):
            st.session_state.selected_note_id = note_id
            st.session_state.selected_note_content = note_content
            st.rerun()


def main():
    load_css("style.css")
    conn, c = init_db()
    st.logo('logo/side_bar.png', icon_image='logo/main_page.png')

    if 'selected_note_id' in st.session_state:
        note_content = st.session_state.selected_note_content
        st.write(note_content)
        st.markdown('---')
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            if st.button('Delete Note'):
                c.execute("DELETE FROM notes WHERE id=?", (st.session_state.selected_note_id,))
                conn.commit()
                del st.session_state.selected_note_id
                del st.session_state.selected_note_content
                st.rerun()

        with col2:
            st.download_button('Save as TXT', save_as_txt(note_content), file_name='notes.txt')
        with col3:
            st.download_button('Save as PDF', save_as_pdf(note_content), file_name='notes.pdf')
        with col4:
            st.download_button('Save as DOCX', save_as_doc(note_content), file_name='notes.docx')
        with col5:
            if st.button('Copy'):
                pyperclip.copy(note_content)
                st.success("Copied")

        st.markdown('---')
        # st.write(note_content)
        custom_prompt = st.text_input("Add more content to these notes:")
        if st.button('Generate More Notes'):
            new_prompt = f"{note_content}\n\n{custom_prompt}"
            with st.spinner('Generating more notes...'):
                additional_notes = get_bot_response(new_prompt)
            updated_notes = f"{note_content}\n\n## Custom Prompt:\n\n*{custom_prompt}*\n\n## Additional Notes\n\n{additional_notes}"
            st.write(updated_notes)
            # if st.button('Save Updated Notes'):
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            c.execute("UPDATE notes SET content=?, timestamp=? WHERE id=?", (updated_notes, timestamp, st.session_state.selected_note_id))
            conn.commit()
            st.success('Notes updated successfully!')
            st.session_state.selected_note_content = updated_notes
            st.rerun()


    else:

        st.title("📝 Turn your photos into notes with AI")
        st.markdown('---')
        option = st.radio('Choose generation method', ('From Images', 'From Links'), index=None)
        # col1, col2 = st.columns(2)

        if option == 'From Images':
            tag = st.multiselect('Select the image belong to', ('General', 'Coding', 'Math', 'Student Notes'))

            uploaded_files = st.file_uploader("📁 Choose images...", type=["jpg", "jpeg", "png"],
                                                  accept_multiple_files=True)

            if uploaded_files:
                    with st.spinner('Taking notes...'):
                        text_list, images = process_images(uploaded_files)
                        combined_text = "\n\n".join(text_list)
                        prompt = generate_prompt(combined_text, images, tag)
                        bot_response = get_bot_response(prompt)
                    st.subheader("Generated Notes")
                    st.write(bot_response)
                    st.markdown('---')
                    col1, col2, col3, col4, col5 = st.columns(5)
                    with col1:
                        st.download_button('Save as TXT', save_as_txt(bot_response), file_name='notes.txt')
                    with col2:
                        st.download_button('Save as PDF', save_as_pdf(bot_response), file_name='notes.pdf')
                    with col3:
                        st.download_button('Save as DOCX', save_as_doc(bot_response), file_name='notes.docx')
                    with col4:
                        if st.button('Copy'):
                            pyperclip.copy(bot_response)
                            st.success("Copied")
                    st.markdown('---')
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    c.execute("INSERT INTO notes (content, timestamp) VALUES (?, ?)", (bot_response, timestamp))
                    conn.commit()
                    st.success('Notes saved in App.')
                    st.markdown('---')

        elif option == 'From Links':
                url = st.text_input("Enter the URL of the blog or YouTube video:")
                user_prompt = st.text_input("Enter the prompt about you Link:")
                # link_type = st.selectbox('Select Link Type', ('Blog', 'YouTube'))
                if st.button('Generate from Link'):
                    with st.spinner('Generating notes...'):
                        prompt = generate_link_prompt(url, user_prompt)
                        bot_response = get_bot_response(prompt)
                    st.subheader("Generated Notes")
                    st.write(bot_response)
                    st.markdown('---')
                    col1, col2, col3, col4, col5 = st.columns(5)
                    with col1:
                        st.download_button('Save as TXT', save_as_txt(bot_response), file_name='notes.txt')
                    with col2:
                        st.download_button('Save as PDF', save_as_pdf(bot_response), file_name='notes.pdf')
                    with col3:
                        st.download_button('Save as DOCX', save_as_doc(bot_response), file_name='notes.docx')
                    with col4:
                        if st.button('Copy'):
                            pyperclip.copy(bot_response)
                            st.success("Copied")
                    st.markdown('---')
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    c.execute("INSERT INTO notes (content, timestamp) VALUES (?, ?)", (bot_response, timestamp))
                    conn.commit()
                    st.success('Notes saved in App.')
                    st.markdown('---')

    display_saved_notes(c, conn)
    conn.close()

if __name__ == "__main__":
    main()
