# NoteMaster AI - FastAPI Component

## Overview

NoteMaster AI's FastAPI component provides a robust backend service for transforming photos into structured notes using AI. It handles image processing, text extraction, and note generation, offering a RESTful API for seamless integration into various applications.

## Features

- **Image Upload**: Accepts multiple image formats for processing.
- **Text Extraction**: Utilizes Tesseract OCR for extracting text from images.
- **AI-Driven Note Generation**: Uses AI models to convert extracted text into organized notes.
- **API Endpoints**: Provides endpoints for image processing, note management, and more.

## Available Models

The FastAPI component supports the following AI models:
- **GPT-3.5 Turbo**
- **GPT-4o**
- **Llama 3**
- **Mixtral 70b**
- **BlackBox**
- **Meta AI**

## Installation Options

### Option 1: Streamlit Only Version (First Release)
If you want to use the app without FastAPI, you can use the first release of NoteMaster AI which is Streamlit-only:
1. Go to the [Releases](https://github.com/codewithdark-git/NoteMaster-AI/releases) page.
2. Download the first release.
3. Follow the installation steps as mentioned on the release page.

### Option 2: Full Version with FastAPI
The current version includes FastAPI for enhanced functionality. Follow the standard installation steps mentioned below to use this version.

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/codewithdark-git/NoteMaster-AI.git
    cd NoteMaster-AI
    ```

2. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

3. Run the API generation script:
    ```bash
    python backend/generate_api.py
    ```

   After running the script, copy the API from `.env` and add it to your frontend configuration.

4. Start the FastAPI server:
    ```bash
    uvicorn fastapi_app:app --reload
    ```

## Usage

1. **Access the API**:
   - The API runs on `http://localhost:8000`
   - Access the interactive API documentation at `http://localhost:8000/docs`

2. **Endpoints**:
   - `POST /generate_from_images`: Generate notes from uploaded images
   - `POST /generate_from_link`: Generate notes from a link
   - `GET /notes/`: Retrieve all notes
   - `DELETE /notes/{note_id}`: Remove notes
   - `POST /follow-up-question/`: Generate a follow-up response based on a saved note

3. **Example Usage**:
   - `curl -X POST -F "files=@image1.jpg" http://localhost:8000/generate_from_images`
   - `curl -X POST -F  http://localhost:8000/generate_from_link`
   - `curl -X GET http://localhost:8000/notes/`
   - `curl -X DELETE http://localhost:8000/notes/{note_id}`
   - `curl -X POST -F "note_id=1" -F "user_prompt=What more can I learn?" http://localhost:8000/follow-up-question/`

## Customization

- **Model Configuration**: Adjust model settings in `fastapi_app.py`.
- **API Behavior**: Modify processing parameters and response formats.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue to discuss your ideas.

## License

This project is licensed under the MIT License.