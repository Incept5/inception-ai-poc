import os
import requests
from flask import Blueprint, jsonify
from utils.debug_utils import debug_print

audio_token_blueprint = Blueprint('audio_token', __name__)

@audio_token_blueprint.route('/audio-token', methods=['GET'])
def get_audio_token():
    api_key = os.getenv('ASSEMBLYAI_API_KEY')
    if not api_key:
        return jsonify({"error": "ASSEMBLYAI_API_KEY not set"}), 500

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
        response.raise_for_status()  # Raises an HTTPError for bad responses
        token = response.json().get('token')
        if token:
            return jsonify({"token": token})
        else:
            return jsonify({"error": "Token not found in response"}), 500
    except requests.RequestException as e:
        debug_print(f"API request failed: {str(e)}")
        return jsonify({"error": f"ASSEMBLYAI_API_KEY not set or other issue with AssemblyAI configuration"}), 400