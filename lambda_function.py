import json
import os
import requests
from typing import Dict

GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
GEMINI_API_URL = 'https://api.gemini.com/v1'

convo_memory: Dict[str, str] = {}

def chat(query: str, user_id: str) -> str:
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not set")
    
    headers = {"Content-Type": "application/json"}
    prev_context = convo_memory.get(user_id, '')
    prompt_text = f"{prev_context} \nUser:{query}" if prev_context else query

    payload = { "prompt": prompt_text, "temperature": 0.5 }
    response = requests.post(f"{GEMINI_API_URL}/chat", headers=headers, json=payload)
    if response.status_code != 200:
        raise ValueError(f"Failed to chat with Gemini: {response.text}")
    
    response_data = response.json()
    bot_response = response_data.get('choices', [{}])[0].get('text', '')
    convo_memory[user_id] = f"{prev_context} \nUser:{query}\nBot:{bot_response}"

    return bot_response

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        query = body['query']
        user_id = body['user_id']

        if not query:
            raise ValueError("Query is required")
        
        result = chat(query, user_id)
        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(str(e))
        }

