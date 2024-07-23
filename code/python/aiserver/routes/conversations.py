from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List
import os
import json
from datetime import datetime

conversations_router = APIRouter()

BASE_DIR = '/data/persisted_files/__conversations'


def debug_print(message):
    print(f"[DEBUG] {message}")


class ConversationData(BaseModel):
    thread_id: str
    label: str


class ConversationResponse(BaseModel):
    thread_id: str
    label: str
    created_at: str


@conversations_router.post('/conversations', response_model=ConversationResponse)
async def store_conversation(data: ConversationData):
    debug_print("Received POST request to store a conversation")

    thread_id = data.thread_id
    label = data.label
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
        return ConversationResponse(**conversation_data)
    except Exception as e:
        debug_print(f"Error storing conversation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error storing conversation: {str(e)}")


@conversations_router.get('/conversations', response_model=List[ConversationResponse])
async def get_conversations():
    debug_print("Received GET request to retrieve conversations")

    try:
        conversations = []
        for filename in os.listdir(BASE_DIR):
            if filename.endswith('.json'):
                file_path = os.path.join(BASE_DIR, filename)
                with open(file_path, 'r') as f:
                    conversation_data = json.load(f)
                    conversations.append(ConversationResponse(**conversation_data))

        # Sort conversations by created_at date in descending order
        conversations.sort(key=lambda x: x.created_at, reverse=True)

        debug_print(f"Retrieved {len(conversations)} conversations")
        return conversations
    except Exception as e:
        debug_print(f"Error retrieving conversations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving conversations: {str(e)}")