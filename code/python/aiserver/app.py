# app.py

import os
from flask import Flask
from flask_cors import CORS
from routes.bot_router import bot_blueprint
from routes.llm_models import llm_models_blueprint
from routes.file_viewer import file_viewer_blueprint
from routes.conversations import conversations_blueprint
from config import Config
from utils.debug_utils import debug_print
from bots.configured_bots import get_configured_bots
from mylangchain.retriever_manager import retriever_manager

def process_pdfs():
    imported_dir = "data/imported"
    if os.path.exists(imported_dir):
        for name in os.listdir(imported_dir):
            retriever_manager.process_pdfs(name)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)

    app.register_blueprint(bot_blueprint)
    app.register_blueprint(llm_models_blueprint)
    app.register_blueprint(file_viewer_blueprint)
    app.register_blueprint(conversations_blueprint)

    # Process PDFs at startup
    process_pdfs()

    # Initialize bot instances
    with app.app_context():
        get_configured_bots()

    return app

# Create the app instance
app = create_app()

if __name__ == '__main__':
    debug_print("Starting Flask app")
    app.run(host='0.0.0.0', port=9871, debug=True)