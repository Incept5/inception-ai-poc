from flask import Blueprint, request, jsonify, current_app
from bots.configured_bots import get_configured_bots
from utils.debug_utils import debug_print

bot_blueprint = Blueprint('bots', __name__)

@bot_blueprint.route('/bots', methods=['GET'])
def get_available_bots():
    """
    Returns a list of available bots with their descriptions and config options for the UI.
    """
    configured_bots = get_configured_bots()
    available_bots = [
        {
            'bot_type': bot_type,
            'description': bot.description,
            'config_options': bot.get_config_options()
        }
        for bot_type, bot in configured_bots.items()
    ]
    return jsonify(available_bots)

@bot_blueprint.route('/bots/<bot_type>', methods=['POST'])
def chat(bot_type):
    debug_print(f"Received POST request to /bots/{bot_type}")
    data = request.json
    debug_print(f"Request data: {data}")

    user_input = data.get('message')
    context = data.get('context', '')
    config = data.get('config', {})

    if not user_input:
        debug_print("Error: No message provided")
        return jsonify({"error": "No message provided"}), 400

    configured_bots = get_configured_bots()
    bot = configured_bots.get(bot_type)
    if bot is None:
        debug_print(f"Error: Invalid bot type {bot_type}")
        return jsonify({"error": f"Invalid bot type {bot_type}"}), 400

    try:
        response = bot.process_request(user_input, context, **config)
        return jsonify({"response": response})
    except Exception as e:
        debug_print(f"Error processing request: {str(e)}")
        return jsonify({"error": f"Error processing request: {str(e)}"}), 500