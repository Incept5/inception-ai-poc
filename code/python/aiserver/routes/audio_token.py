import os
import requests
import time
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from utils.debug_utils import debug_print

audio_token_router = APIRouter()

# Global variables to store the token and its expiry time
current_token = None
token_expiry_time = 0

def fetch_new_token():
    api_key = os.getenv('ASSEMBLYAI_API_KEY')
    if not api_key:
        raise ValueError("ASSEMBLYAI_API_KEY not set")

    url = "https://api.assemblyai.com/v2/realtime/token"
    headers = {
        "authorization": api_key,
        "Content-Type": "application/json"
    }
    data = {
        "expires_in": 3600  # Token expires in 1 hour (3600 seconds)
    }

    try:
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        token = response.json().get('token')
        if not token:
            raise ValueError("Token not found in response")
        return token
    except requests.RequestException as e:
        debug_print(f"API request failed: {str(e)}")
        raise

class AudioTokenResponse(BaseModel):
    token: str

@audio_token_router.get('/audio-token', response_model=AudioTokenResponse)
async def get_audio_token():
    global current_token, token_expiry_time

    current_time = time.time()

    # Check if we need to fetch a new token
    if current_token is None or current_time >= token_expiry_time:
        try:
            current_token = fetch_new_token()
            token_expiry_time = current_time + 3540  # Set expiry to 59 minutes (3540 seconds) to allow for some buffer
            debug_print("Fetched new audio token")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return AudioTokenResponse(token=current_token)