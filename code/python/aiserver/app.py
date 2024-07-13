# app.py

import os
import threading
from flask import Flask
from flask_cors import CORS
from routes import register_routes
from config import Config
from utils.debug_utils import debug_print
from bots.configured_bots import get_configured_bots
from mylangchain.retriever_manager import retriever_manager

def run_check_imports():
    retriever_manager.check_imports()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)

    register_routes(app)

    # Initialize bot instances
    with app.app_context():
        get_configured_bots()

    # Start check_imports in a background thread
    check_imports_thread = threading.Thread(target=run_check_imports)
    check_imports_thread.start()

    return app

# Create the app instance
app = create_app()

if __name__ == '__main__':
    debug_print("Starting Flask app")
    app.run(host='0.0.0.0', port=9871, debug=True)