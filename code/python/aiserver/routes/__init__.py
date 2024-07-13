from .bot_router import bot_router_bp
from .conversations import conversations_bp
from .file_viewer import file_viewer_bp
from .llm_models import llm_models_bp
from .transcribe_audio import transcribe_audio_bp

def register_routes(app):
    app.register_blueprint(bot_router_bp)
    app.register_blueprint(conversations_bp)
    app.register_blueprint(file_viewer_bp)
    app.register_blueprint(llm_models_bp)
    app.register_blueprint(transcribe_audio_bp)