from collections import OrderedDict
from bots.simple_bot import SimpleBot
from bots.web_search_bot import WebSearchBot
from bots.ollama_bot import OllamaBot

def get_configured_bots():
    # Use OrderedDict to maintain the specified order of bots
    return OrderedDict([
        ("simple-bot", SimpleBot()),
        ("web-search-bot", WebSearchBot()),
        ("ollama-bot", OllamaBot())
    ])