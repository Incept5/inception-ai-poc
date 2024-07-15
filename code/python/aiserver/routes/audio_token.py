import os
from flask import Blueprint, jsonify
from assemblyai import AssemblyAI

audio_token_blueprint = Blueprint('audio_token', __name__)

@audio_token_blueprint.route('/audio-token', methods=['GET'])
def get_audio_token():
    api_key = os.getenv('ASSEMBLYAI_API_KEY')
    if not api_key:
        return jsonify({"error": "ASSEMBLYAI_API_KEY not set"}), 500

    aai = AssemblyAI(api_key=api_key)
    try:
        token = aai.realtime.create_temporary_token(expires_in=3600)
        return jsonify({"token": token})
    except Exception as e:
        return jsonify({"error": str(e)}), 500