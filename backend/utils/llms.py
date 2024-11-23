import g4f.cookies
from g4f.client import Client
import streamlit as st
import base64


# Dictionary mapping model names to provider names
model_provider_mapping = {
    'gpt-4o': None,
    'mixtral_8x7b': 'HuggingFace',
    'blackbox': 'Blackbox',
    'meta': 'MetaAI',
    'llama3_70b_instruct': 'MetaAI',
    # Add more models and providers as needed
}

# Dictionary mapping display model names to internal model names
display_model_mapping = {
    'gpt 4o': 'gpt-4o',
    'llama 3': 'llama3_70b_instruct',
    'Mixtral 70b': 'mixtral_8x7b',
    'BlackBox': 'blackbox',
    'Meta AI': 'meta',
}


def get_provider(model: str) -> str:
    """Get provider name based on the model."""
    return model_provider_mapping.get(model, '')


def get_model(display_model: str) -> str:
    """Get internal model name based on the display model name."""
    return display_model_mapping.get(display_model, '')


def generate_prompt(combined_text, tags):
    prompts = {
        "General": "Create comprehensive notes that summarize the content clearly and concisely.",
        "Coding": "Create detailed notes focusing on coding concepts and examples from the text.",
        "Math": "Create structured notes explaining mathematical concepts and problems from the text.",
        "Student Notes": "Create well-organized notes that highlight important points for students."
    }

    specific_prompts = "\n".join([f"Specific instructions for {tag} images:\n{prompts[tag]}" for tag in tags])

    prompt = f"""
    You are an expert note-taker. For the uploaded {', '.join(tags)} images, generate a title and notes that capture important
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
     generate a title and notes that capture important information across various fields. Your task is to extract 
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


def get_bot_response(prompt, internal_model, provider_name):
    try:
        client = Client()
        response = client.chat.completions.create(
            model=internal_model,
            messages=[{"role": "user", "content": prompt}],
            provider=provider_name,
            cookies=g4f.cookies.get_cookies('bing')
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f'Error generating response.{e}')


