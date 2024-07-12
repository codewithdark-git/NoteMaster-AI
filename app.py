import streamlit as st
from PIL import Image
import numpy as np
import io
import datetime
from utils.helper import save_btn
from utils.ocr import image_to_text
from utils.llms import (
    get_bot_response,
    display_model_mapping,
    get_model, get_provider,
    generate_prompt,
    generate_link_prompt
)
from utils.db import init_db


def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def process_images(uploaded_files):
        images = []
        text_list = []
        for uploaded_file in uploaded_files:
            image = Image.open(uploaded_file)
            image_array = np.array(image)
            if image.mode == 'RGBA':
                image = image.convert('RGB')
            extracted_text = image_to_text(image_array)
            text_list.append(str(extracted_text))
            images.append(image)
            st.success('Processed Image Successfully!')
            st.balloons()
        return text_list, images


def display_saved_notes(c, conn):
    st.sidebar.title("Saved Notes")
    c.execute("SELECT id, content, image FROM notes ORDER BY timestamp DESC")
    rows = c.fetchall()
    for row in rows:
        note_id, note_content, image_data = row
        title = note_content.split('\n', 1)[0]
        if st.sidebar.button(title, key=note_id):
            st.session_state.selected_note_id = note_id
            st.session_state.selected_note_content = note_content
            st.session_state.selected_note_image = image_data
            st.rerun()


def main():
    st.set_page_config('NoteMasterAI', page_icon="random", layout="centered", initial_sidebar_state="auto")
    load_css("style.css")
    conn, c = init_db()
    st.markdown("""
        <div class="title">
         Turn your <span>Photos, Links</span> into <span>Notes</span> with <span>NoteMasterAi</span>
        </div>
        """, unsafe_allow_html=True)
    # st.logo('logo/side_bar.png', icon_image='logo/main_page.png')

    display_model = st.sidebar.selectbox("Select Model", list(display_model_mapping.keys()), index=0)
    internal_model = get_model(display_model)
    provider_name = get_provider(internal_model)

    if 'selected_note_id' in st.session_state:
        note_content = st.session_state.selected_note_content
        note_image = st.session_state.selected_note_image
        # title = note_content.split("\n", 1)[0]
        # st.subheader(str(title).replace("[ ' ' ]", " "))
        st.markdown('---')
        if note_image:
            image = Image.open(io.BytesIO(note_image))
            st.image(image, caption='Saved Image', use_column_width=True)
        st.write(note_content)
        st.markdown('---')
        if st.button('Delete Note'):
            c.execute("DELETE FROM notes WHERE id=?", (st.session_state.selected_note_id,))
            conn.commit()
            del st.session_state.selected_note_id
            del st.session_state.selected_note_content
            del st.session_state.selected_note_image
            st.toast('Notes Deleted', icon='☠️')
            st.rerun()
        try:
            save_btn(note_content)
        except Exception as e:
            st.error(f'Error Occur Try Again: {e}')
        custom_prompt = st.chat_input("Add more content to these notes:")
        if custom_prompt:
            new_prompt = f"{note_content}\n\n{custom_prompt}"
            with st.spinner(f'{custom_prompt} ....'):
                additional_notes = get_bot_response(new_prompt, internal_model, provider_name)
            updated_notes = f"{note_content}\n\n#### Your Prompt:\n {custom_prompt}\n\n### Additional Notes\n\n{additional_notes}"
            st.write(updated_notes)
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            c.execute("UPDATE notes SET content=?, timestamp=? WHERE id=?",
                      (updated_notes, timestamp, st.session_state.selected_note_id))
            conn.commit()
            st.toast('Notes updated successfully!', icon='🎊')
            st.session_state.selected_note_content = updated_notes
            st.rerun()

    else:
        option = st.radio('Select Option to Generate :', ('Generate From Images', 'Generate From Links'), index=None)
        if option == 'Generate From Images':
            tag = st.multiselect('Select the image belong to', ('General', 'Coding', 'Math', 'Student Notes'))

            uploaded_files = st.file_uploader("📁 Choose images...", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

            all_files = []
            if uploaded_files:
                all_files.extend(uploaded_files)

            if all_files:
                with st.spinner('Taking notes...'):
                    text_list, images = process_images(all_files)
                    combined_text = "\n\n".join(text_list)
                    prompt = generate_prompt(combined_text, tag)
                    try:
                        bot_response = get_bot_response(prompt, internal_model, provider_name)
                    except Exception as e:
                        st.error(f'Error generating bot response {e}')
                st.markdown('---')
                for img in images:
                    st.image(img, caption='Uploaded Image', use_column_width=True)
                st.write(bot_response)
                try:
                    save_btn(bot_response)
                except Exception as e:
                    st.error(f'Error Occur Try Again: {e}')
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                for img in images:
                    buffered = io.BytesIO()
                    img.save(buffered, format="JPEG")
                    img_str = buffered.getvalue()
                    c.execute("INSERT INTO notes (content, image, timestamp) VALUES (?, ?, ?)",
                              (bot_response, img_str, timestamp))
                conn.commit()
                st.toast('Notes saved in App.', icon='🎊')

        elif option == 'Generate From Links':
            url = st.text_input("Enter the URL of the blog or YouTube video:")
            user_prompt = st.chat_input("Enter the prompt about your Link:").capitalize()
            if user_prompt:
                with st.spinner(f'*{user_prompt}* \n {url}'):
                    prompt = generate_link_prompt(url, user_prompt)
                    bot_response = get_bot_response(prompt, internal_model, provider_name)
                st.markdown('----')
                st.chat_message("user").write(f'*{user_prompt}* \n {url}')
                st.write(bot_response)
                try:
                    save_btn(bot_response)
                except Exception as e:
                    st.error(f'Error Occur Try Again: {e}')
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                c.execute("INSERT INTO notes (content, timestamp) VALUES (?, ?)", (bot_response, timestamp))
                conn.commit()
                st.toast('Notes saved in App.', icon='🎉')
                st.markdown('---')

    display_saved_notes(c, conn)
    conn.close()


if __name__ == "__main__":
    main()
