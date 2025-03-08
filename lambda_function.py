import json
import os
import logging
from typing import Dict
from google import genai

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Load your Gemini API key from environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise Exception("Gemini API key not found.")

# Create a Gemini client instance for reuse
client = genai.Client(api_key=GEMINI_API_KEY)

# In-memory conversation memory (for demo purposes; note that state in Lambda is ephemeral)
conversation_memory: Dict[str, str] = {}

def chat(query: str, user_id: str) -> Dict[str, str]:
    """
    Process a chat query using the Gemini API and maintain a simple conversation memory.
    """
    previous_context = conversation_memory.get(user_id, "")
    prompt_text = f"Previous conversation: {previous_context}\nUser: {query}" if previous_context else query

    try:
        # Use the official Gemini client to generate a response.
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt_text,
        )
    except Exception as e:
        logger.error("Gemini API error: %s", e)
        raise Exception(f"Gemini API error: {e}")

    # Assume the API response object has a 'text' attribute for the generated response.
    bot_response = response.text if hasattr(response, "text") else "No response"

    # Update the conversation memory (for demo purposes only).
    if previous_context:
        conversation_memory[user_id] = f"{previous_context}\nUser: {query}\nBot: {bot_response}"
    else:
        conversation_memory[user_id] = f"User: {query}\nBot: {bot_response}"

    return {"response": bot_response}

def lambda_handler(event, context):
    """
    AWS Lambda handler that expects a JSON body with 'query' and an optional 'user_id'.
    """
    try:
        body = json.loads(event.get("body", "{}"))
        query = body.get("query", "")
        user_id = body.get("user_id", "default_user")

        if not query:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Query parameter is missing."}),
                "headers": {"Content-Type": "application/json"}
            }

        result = chat(query, user_id)
        return {
            "statusCode": 200,
            "body": json.dumps(result),
            "headers": {"Content-Type": "application/json"}
        }
    except Exception as e:
        logger.exception("Error processing the request")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)}),
            "headers": {"Content-Type": "application/json"}
        }
