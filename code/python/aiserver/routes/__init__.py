from fastapi import APIRouter
from .bot_router import bot_router
from .llm_models import llm_models_router
from .file_viewer import file_viewer_router
from .file_updater import file_updater_router
from .conversations import conversations_router
from .audio_token import audio_token_router

combined_routes = APIRouter()

# Include all routers
combined_routes.include_router(bot_router)
combined_routes.include_router(llm_models_router)
combined_routes.include_router(file_viewer_router)
combined_routes.include_router(file_updater_router)
combined_routes.include_router(conversations_router)
combined_routes.include_router(audio_token_router)