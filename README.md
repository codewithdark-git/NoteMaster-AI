# Enhanced Note Generator

## Overview

The Enhanced Note Generator is a Streamlit application that converts images into well-structured notes using OCR and GPT-4. It supports multiple image uploads, provides various download options, and includes a feature to save notes to Google Docs.

## Features

- **Multiple Image Upload**: Users can upload multiple images in JPG, JPEG, or PNG format.
- **Image to Text Conversion**: Extracts text from images using Tesseract OCR.
- **AI-Powered Note Generation**: Organizes extracted text into structured notes using GPT-4.
- **Math Problem Solving**: Identifies and solves math-related content from images.
- **Download Options**: Save notes as TXT, PDF, or DOCX files.
- **Copy to Clipboard**: Easily copy generated notes to the clipboard.


## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/codewithdark-git/NoteMaster-AI.git
    cd NoteMaster AI
    ```

2. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

3. Download Tesseract OCR from [here](https://github.com/tesseract-ocr/tesseract).

5. Run the Streamlit app:
    ```bash
    streamlit run app.py
    ```

## Usage

1. Upload one or more images by clicking on "📁 Choose images...".
2. Wait for the images to be processed and text to be extracted.
3. View the generated notes in the "Generated Notes" section.
4. Choose to download the notes as TXT, PDF, or DOCX, copy them to the clipboard, or save them to Google Docs.

## Customization

You can customize the app by modifying the following components:

- **CSS Styling**: Adjust the styles in the `st.markdown` block to change the appearance of the app.
- **Prompt Configuration**: Modify the prompt in the `prompt` variable to adjust the note-taking instructions given to the AI.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue to discuss your ideas.

## License

This project is licensed under the MIT License.
