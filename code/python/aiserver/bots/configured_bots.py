from flask import current_app
from collections import OrderedDict
from bots.simple_bot import SimpleBot
from bots.web_search_bot import WebSearchBot
from bots.ollama_bot import OllamaBot


def get_configured_bots():
    # Check if bots are already stored in the app context
    if 'configured_bots' not in current_app.extensions:
        # If not, create new instances and store them
        bots = OrderedDict([
            ("simple-bot", SimpleBot()),
            ("web-search-bot", WebSearchBot()),
            ("ollama-bot", OllamaBot())
        ])
        current_app.extensions['configured_bots'] = bots

    # Return the stored bots
    return current_app.extensions['configured_bots']