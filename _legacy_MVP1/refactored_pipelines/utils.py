import os
import logging
import time
import json
from dotenv import load_dotenv
from supabase import create_client, Client
import google.generativeai as genai

# --- Environment Loading ---

def load_environment():
    """
    Loads environment variables from a .env file in the project root.
    Project root is assumed to be two levels up from this script's directory.
    """
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    dotenv_path = os.path.join(project_root, '.env')
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)
    else:
        # Use a logger if available, otherwise print
        try:
            logger = get_logger(__name__)
            logger.warning(f".env file not found at {dotenv_path}. Ensure environment variables are set.")
        except NameError:
            print(f"Warning: .env file not found at {dotenv_path}. Make sure to set environment variables manually.")

# --- Logging ---

def get_logger(name: str, level=logging.INFO) -> logging.Logger:
    """
    Returns a configured logger instance.
    """
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            # logging.FileHandler("pipeline.log")
        ]
    )
    return logging.getLogger(name)

# --- Client Initialization ---

_supabase_client = None
def get_supabase_client() -> Client:
    """Initializes and returns a Supabase client, caching it for subsequent calls."""
    global _supabase_client
    if _supabase_client is None:
        load_environment()
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_ANON_KEY")
        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set in your environment.")
        _supabase_client = create_client(url, key)
    return _supabase_client

_generative_model = None
def get_gemini_model():
    """Initializes and returns a Google Gemini Pro model instance, caching it."""
    global _generative_model
    if _generative_model is None:
        load_environment()
        api_key = os.environ.get("GOOGLE_API_KEY") # Or your specific Gemini key env var
        if not api_key:
            raise ValueError("GOOGLE_API_KEY must be set in your environment.")
        genai.configure(api_key=api_key)
        _generative_model = genai.GenerativeModel('gemini-pro')
    return _generative_model

# --- Shared LLM Calls ---

def call_gemini_with_retry(prompt: str, retries: int = 3) -> str | None:
    """Calls the Gemini model with a prompt and handles retries."""
    logger = get_logger(__name__)
    try:
        model = get_gemini_model()
        generation_config = {
            "temperature": 0.3, "topP": 0.95, "topK": 40, "maxOutputTokens": 16384,
        }
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
        ]
        for attempt in range(retries):
            try:
                response = model.generate_content(
                    contents=prompt,
                    generation_config=generation_config,
                    safety_settings=safety_settings
                )
                return response.text.strip()
            except Exception as e:
                logger.warning(f"Gemini API call failed on attempt {attempt + 1}: {e}")
                if attempt < retries - 1:
                    wait_time = 2 ** (attempt + 1)
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error("Gemini API call failed after all retries.")
                    return None
    except Exception as e:
        logger.error(f"Failed to initialize Gemini model: {e}")
        return None

def generate_headlines_batch(topics_data: list) -> list:
    """Generates multiple headlines in one LLM call."""
    logger = get_logger(__name__)
    if not topics_data:
        return []

    topics_text = ""
    for i, topic in enumerate(topics_data, 1):
        titles = "\n    ".join(f"- {t}" for t in topic['article_titles'][:3])
        topics_text += f"\n{i}. Topic: {topic['name']}\n   Articles:\n    {titles}\n"
    
    prompt = f"""You are a witty and sensible editor for 'News Spectrum', a Gen-Z targeted news service.
Your goal is to rewrite hard news titles into engaging, conversational Korean headlines, while maintaining journalistic integrity.
AVOID noun-endings. Use complete sentences or questions. Keep it under 45 chars.
NO CLICKBAIT. Emojis are okay if relevant.

Input Topics:
{topics_text}

Output Format (JSON with a 'headlines' key):
{{
    "headlines": [
        "Headline 1",
        "Headline 2",
        ...
    ]
}}"""
    
    response_text = call_gemini_with_retry(prompt)
    if not response_text:
        return [topic['name'][:50] for topic in topics_data]

    try:
        if "```json" in response_text:
            text = response_text.split("```json")[1].split("```")[0]
        else:
            text = response_text
        result = json.loads(text)
        headlines = result.get('headlines', [])
    except Exception:
        logger.warning("Failed to parse JSON from headline generation, falling back to line-by-line parsing.")
        lines = [line.strip() for line in response_text.split('\n') if line.strip()]
        headlines = []
        for line in lines:
            if line.endswith(':') or "Here are" in line: continue
            if line[0].isdigit():
                line = line.split('.', 1)[1].strip() if '.' in line else line
            if line.startswith('"') and line.endswith('"'):
                line = line[1:-1]
            headlines.append(line)
            
    if len(headlines) < len(topics_data):
        headlines.extend([t['name'][:50] for t in topics_data[len(headlines):]])
    elif len(headlines) > len(topics_data):
        headlines = headlines[-len(topics_data):]
        
    return headlines

if __name__ == '__main__':
    # Example usage and self-test
    print("Running utility self-test...")
    logger = get_logger(__name__)
    logger.info("Logger initialized.")
    try:
        supabase = get_supabase_client()
        logger.info("Supabase client initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize Supabase client: {e}")
    try:
        model = get_gemini_model()
        logger.info("Gemini model initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize Gemini model: {e}")
    print("Utility self-test finished.")