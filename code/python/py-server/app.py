# app.py

from flask import Flask
from flask_cors import CORS
from routes.bots.bot_router import bot_blueprint
from routes.llm_models import llm_models_blueprint
from config import Config
from utils.debug_utils import debug_print

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

app.register_blueprint(bot_blueprint)
app.register_blueprint(llm_models_blueprint)

if __name__ == '__main__':
    debug_print("Starting Flask app")
    app.run(host='0.0.0.0', port=5010, debug=True)