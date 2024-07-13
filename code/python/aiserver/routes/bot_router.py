from flask import Blueprint, request, jsonify, current_app, Response, stream_with_context
from bots.configured_bots import get_configured_bots
from utils.debug_utils import debug_print
import json

bot_router_bp = Blueprint('bots', __name__)

@bot_router_bp.route('/bots', methods=['GET'])
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

@bot_router_bp.route('/bots/<bot_type>', methods=['POST'])
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

    def generate():
        try:
            for response in bot.process_request(user_input, context, **config):
                yield f"data: {json.dumps(response)}\n\n"
        except Exception as e:
            debug_print(f"Error processing request: {str(e)}")
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
        yield "data: [DONE]\n\n"

    return Response(stream_with_context(generate()), content_type='text/event-stream')