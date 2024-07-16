from flask import Blueprint
from .bot_router import bot_blueprint
from .llm_models import llm_models_blueprint
from .file_viewer import file_viewer_blueprint
from .file_updater import file_updater_blueprint
from .conversations import conversations_blueprint
from .audio_token import audio_token_blueprint

combined_routes = Blueprint('combined_routes', __name__)

# Register all blueprints with the combined_routes
combined_routes.register_blueprint(bot_blueprint)
combined_routes.register_blueprint(llm_models_blueprint)
combined_routes.register_blueprint(file_viewer_blueprint)
combined_routes.register_blueprint(file_updater_blueprint)
combined_routes.register_blueprint(conversations_blueprint)
combined_routes.register_blueprint(audio_token_blueprint)