from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends, Security
from fastapi.responses import JSONResponse
from typing import List
from backend.utils.helper import process_images, save_btn
from backend.utils.web_agent import web_agent_flow
from backend.utils.llms import (
    get_bot_response, generate_prompt, 
    generate_link_prompt, display_model_mapping,
    get_model, get_provider, follow_up_Q
) 
from backend.utils.db import init_db
from PIL import Image
from fastapi import UploadFile
import datetime
import os
import io
import base64
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security.api_key import APIKeyHeader

# Load environment variables from api.env
load_dotenv("api.env")

app = FastAPI()

# Configure CORS
origins = [
    "http://localhost",
    "http://localhost:8501",  # Default Streamlit port
    "*",  # Allow all origins
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
conn, c = init_db()

# API Key security
API_KEY = os.getenv("ApiKey")
api_key_header = APIKeyHeader(name="X-API-Key")

def get_api_key(api_key: str = Security(api_key_header)):
    if api_key == API_KEY:
        return api_key
    raise HTTPException(
        status_code=401,
        detail="Invalid API Key"
    )

@app.on_event("shutdown")
async def shutdown_event():
    conn.close()

@app.post("/generate-from-images/")
async def generate_from_images(
    files: List[UploadFile] = File(...),
    tags: List[str] = Form(default=["General"]),
    model: str = Form(default="gpt-4o"),
    api_key: str = Depends(get_api_key)
):
    try:
        # Process uploaded files
        all_files = []
        for file in files:
            try:
                contents = await file.read()
                image_stream = io.BytesIO(contents)
                all_files.append(image_stream)
            except Exception as file_error:
                raise HTTPException(
                    status_code=400,
                    detail=f"Error processing file {file.filename}: {str(file_error)}"
                )

        if not all_files:
            raise HTTPException(status_code=400, detail="No valid images provided")

        try:
            # Get model and provider information
            internal_model = get_model(model) or model
            provider_name = get_provider(internal_model)

            # Validate and normalize tags
            valid_tags = ["General", "Coding", "Math", "Student Notes"]
            normalized_tags = [tag if tag in valid_tags else "General" for tag in tags]

            # Process the images
            text_list, processed_images = process_images(all_files)
            if not text_list:
                raise HTTPException(status_code=400, detail="Could not extract text from images")

            # Clean and join the text
            text_list = [text for text in text_list if text and text.strip()]
            if not text_list:
                raise HTTPException(status_code=400, detail="No valid text extracted from images")
                
            combined_text = "\n\n".join(text_list)
            prompt = generate_prompt(combined_text, normalized_tags)
            bot_response = get_bot_response(prompt, internal_model, provider_name)

            if not bot_response:
                raise HTTPException(status_code=500, detail="Failed to generate response")

            # Store in database
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            base64_images = []
            for img in processed_images:
                buffered = io.BytesIO()
                img.save(buffered, format="JPEG")
                img_str = buffered.getvalue()
                buffered.close()

                # Convert image bytes to Base64
                img_base64 = base64.b64encode(img_str).decode('utf-8')
                base64_images.append(img_base64)
                
                c.execute(
                    "INSERT INTO notes (content, image, timestamp) VALUES (?, ?, ?)",
                    (bot_response, img_str, timestamp)
                )

            conn.commit()

            return JSONResponse(
                content={
                    "message": "Notes generated and saved successfully",
                    "response": bot_response,
                    "timestamp": timestamp,
                    "image_count": len(processed_images),
                    "images": base64_images  # Include Base64 images in response
                },
                status_code=200
            )

        except Exception as process_error:
            raise HTTPException(
                status_code=500,
                detail=f"Error processing images: {str(process_error)}"
            )

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )

@app.post("/generate-from-link/")
async def generate_from_link(url: str = Form(...), api_key: str = Depends(get_api_key)):
    try:
        bot_response = web_agent_flow(url)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute("INSERT INTO notes (content, timestamp) VALUES (?, ?)", (bot_response, timestamp))
        conn.commit()
        return JSONResponse(content={"message": "Notes generated and saved.", "response": bot_response})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/notes/")
async def get_notes(api_key: str = Depends(get_api_key)):
    try:
        c.execute("SELECT id, content, image, timestamp FROM notes")
        rows = c.fetchall()

        # Convert images to Base64
        notes = []
        for row in rows:
            note_id, content, image_bytes, timestamp = row
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
            notes.append({
                "id": note_id,
                "content": content,
                "image": image_base64,
                "timestamp": timestamp
            })

        return JSONResponse(content={"notes": notes})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.delete("/notes/{note_id}")
async def delete_note(note_id: int, api_key: str = Depends(get_api_key)):
    try:
        c.execute("DELETE FROM notes WHERE id=?", (note_id,))
        conn.commit()
        return JSONResponse(content={"message": "Note deleted."})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/follow-up-question/")
async def follow_up_question(note_id: int = Form(...), user_prompt: str = Form(...), api_key: str = Depends(get_api_key)):
    try:
        # Fetch the specific note from the database
        c.execute("SELECT content FROM notes WHERE id=?", (note_id,))
        row = c.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Note not found.")

        note_content = row[0]

        # Generate follow-up response using follow_up_Q function
        prompt = follow_up_Q(user_prompt, note_content)
        follow_up_response = get_bot_response(prompt)

        if not follow_up_response:
            raise HTTPException(status_code=500, detail="Failed to generate follow-up response.")

        # Update the note in the database by appending new content to the old content
        c.execute("UPDATE notes SET content = content || ? WHERE id=?", (f"### follow-up response:\n{follow_up_response}", note_id))
        conn.commit()

        return JSONResponse(content={"follow_up_response": follow_up_response})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
