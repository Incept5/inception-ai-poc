# app.py

from flask import Flask
from flask_cors import CORS
from routes.chat import chat_blueprint
from routes.ollama_api import ollama_blueprint
from config import Config
from utils.debug_utils import debug_print

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

app.register_blueprint(chat_blueprint)
app.register_blueprint(ollama_blueprint)

if __name__ == '__main__':
    debug_print("Starting Flask app")
    app.run(host='0.0.0.0', port=5010, debug=True)