from fastapi import APIRouter, Depends
from .bot_router import create_bot_router
from .llm_models import llm_models_router
from .file_viewer import file_viewer_router
from .file_updater import file_updater_router
from .conversations import conversations_router
from .audio_token import audio_token_router

def include_all_routers(app):

    # This one needs a dependency on the app for configured bots
    app.include_router(create_bot_router(app))
    app.include_router(llm_models_router)
    app.include_router(file_viewer_router)
    app.include_router(file_updater_router)
    app.include_router(conversations_router)
    app.include_router(audio_token_router)

