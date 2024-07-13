from flask import Blueprint, jsonify, request
import os
import json
from datetime import datetime

conversations_bp = Blueprint('conversations', __name__)

BASE_DIR = '/data/persisted_files/__conversations'

def debug_print(message):
    print(f"[DEBUG] {message}")

@conversations_bp.route('/conversations', methods=['POST'])
def store_conversation():
    debug_print("Received POST request to store a conversation")

    data = request.json
    if not data or 'thread_id' not in data or 'label' not in data:
        debug_print("Invalid request data")
        return jsonify({"error": "Invalid request. 'thread_id' and 'label' are required."}), 400

    thread_id = data['thread_id']
    label = data['label']
    created_at = datetime.utcnow().isoformat()

    # Ensure the directory exists
    os.makedirs(BASE_DIR, exist_ok=True)

    file_path = os.path.join(BASE_DIR, f"{thread_id}.json")
    
    try:
        conversation_data = {
            "thread_id": thread_id,
            "label": label,
            "created_at": created_at
        }
        with open(file_path, 'w') as f:
            json.dump(conversation_data, f)
        debug_print(f"Conversation stored successfully: {file_path}")
        return jsonify({"message": "Conversation stored successfully", "conversation": conversation_data}), 200
    except Exception as e:
        debug_print(f"Error storing conversation: {str(e)}")
        return jsonify({"error": f"Error storing conversation: {str(e)}"}), 500

@conversations_bp.route('/conversations', methods=['GET'])
def get_conversations():
    debug_print("Received GET request to retrieve conversations")

    try:
        conversations = []
        for filename in os.listdir(BASE_DIR):
            if filename.endswith('.json'):
                file_path = os.path.join(BASE_DIR, filename)
                with open(file_path, 'r') as f:
                    conversation_data = json.load(f)
                    conversations.append(conversation_data)

        # Sort conversations by created_at date in descending order
        conversations.sort(key=lambda x: x['created_at'], reverse=True)

        debug_print(f"Retrieved {len(conversations)} conversations")
        return jsonify(conversations), 200
    except Exception as e:
        debug_print(f"Error retrieving conversations: {str(e)}")
        return jsonify({"error": f"Error retrieving conversations: {str(e)}"}), 500

# Add this blueprint to your app.py
# from routes.conversations import conversations_blueprint
# app.register_blueprint(conversations_blueprint, url_prefix='/api')