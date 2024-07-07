from flask import current_app
from collections import OrderedDict
from bots.simple_bot import SimpleBot
from bots.web_search_bot import WebSearchBot
from bots.ollama_bot import OllamaBot
from bots.system_improver_bot import SystemImproverBot
from bots.web_enabled_improver_bot import WebEnabledImproverBot
from bots.web_app_bot import WebAppBot

def get_configured_bots():
    # Check if bots are already stored in the app context
    if 'configured_bots' not in current_app.extensions:
        # If not, create new instances and store them
        bots = OrderedDict([
            ("system-improver-bot", SystemImproverBot()),
            ("web-enabled-improver-bot", WebEnabledImproverBot()),
            ("web-app-bot", WebAppBot()),
            ("simple-bot", SimpleBot()),
            ("web-search-bot", WebSearchBot()),
            ("ollama-bot", OllamaBot())
        ])
        current_app.extensions['configured_bots'] = bots

    # Return the stored bots
    return current_app.extensions['configured_bots']