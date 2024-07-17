from flask import current_app
from collections import OrderedDict
from bots.simple_bot import SimpleBot
from bots.web_search_bot import WebSearchBot
from bots.ollama_bot import OllamaBot
from bots.system_improver_bot import SystemImproverBot
from bots.web_app_bot import WebAppBot
from bots.simple_retriever_bot import SimpleRetrieverBot
from bots.iso20022_expert_bot import ISO20022ExpertBot
from bots.system_bots import SystemBotManager
from bots.collaboration_agent_bot import CollaborationAgentBot

def get_configured_bots():
    # Check if bots are already stored in the app context
    if 'configured_bots' not in current_app.extensions:
        # If not, create new instances and store them
        bots = OrderedDict([
            ("system-improver-bot", SystemImproverBot()),
            ("web-app-bot", WebAppBot()),
            ("simple-bot", SimpleBot()),
            ("web-search-bot", WebSearchBot()),
            ("ollama-bot", OllamaBot()),
            ("simple-retriever-bot", SimpleRetrieverBot()),
            ("iso20022-expert-bot", ISO20022ExpertBot()),
            ("collaboration-agent-bot", CollaborationAgentBot())
        ])
        current_app.extensions['configured_bots'] = bots

    # Return the stored bots
    return current_app.extensions['configured_bots']

def get_bot(bot_type):
    configured_bots = get_configured_bots()
    if bot_type in configured_bots:
        return configured_bots[bot_type]
    else:
        return SystemBotManager.get_system_bot(bot_type)

def get_all_bots():
    configured_bots = get_configured_bots()
    system_bots = SystemBotManager.get_all_system_bots()
    return {**configured_bots, **system_bots}