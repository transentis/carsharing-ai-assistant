import os
from openai import OpenAI
from dotenv import load_dotenv

def verify_assistant():
    """
    Verify that the assistant ID in the environment variables is valid.
    
    Returns:
        tuple: (bool, str) - Success status and message
    """
    load_dotenv()
    
    assistant_id = os.getenv("OPENAI_ASSISTANT_ID")
    if not assistant_id:
        return False, "OPENAI_ASSISTANT_ID is not set in the environment variables"
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return False, "OPENAI_API_KEY is not set in the environment variables"
    
    client = OpenAI(api_key=api_key)
    
    try:
        # Try to retrieve the assistant
        assistant = client.beta.assistants.retrieve(assistant_id=assistant_id)
        return True, f"Successfully connected to assistant: {assistant.name}"
    except Exception as e:
        return False, f"Error connecting to assistant: {str(e)}"