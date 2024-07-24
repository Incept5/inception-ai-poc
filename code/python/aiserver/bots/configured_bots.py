from collections import OrderedDict
from fastapi import FastAPI
from bots.simple_bot import SimpleBot
from bots.web_search_bot import WebSearchBot
from bots.ollama_bot import OllamaBot
from bots.system_improver_bot import SystemImproverBot
from bots.web_app_bot import WebAppBot
from bots.simple_retriever_bot import SimpleRetrieverBot
from bots.iso20022_expert_bot import ISO20022ExpertBot
from bots.collaboration_agent_bot import CollaborationAgentBot
from bots.fast_mlx_bot import FastMlxBot
from bots.simple_db_bot import SimpleDBBot
from bots.simple.company_search_bot import CompanySearchBot
from bots.advanced_company_search_bot import AdvancedCompanySearchBot
from bots.webscraping_bot import WebScrapingBot

def get_configured_bots():
    return OrderedDict([
        ("system-improver-bot", SystemImproverBot()),
        ("web-app-bot", WebAppBot()),
        ("simple-bot", SimpleBot()),
        ("web-search-bot", WebSearchBot()),
        ("ollama-bot", OllamaBot()),
        ("simple-retriever-bot", SimpleRetrieverBot()),
        ("iso20022-expert-bot", ISO20022ExpertBot()),
        ("collaboration-agent-bot", CollaborationAgentBot()),
        ("fast-mlx-bot", FastMlxBot()),
        ("simple-db-bot", SimpleDBBot()),
        ("company-search-bot", CompanySearchBot()),
        ("advanced-company-search-bot", AdvancedCompanySearchBot()),
        ("webscraping-bot", WebScrapingBot())
    ])


def get_bot(app: FastAPI, bot_type: str):
    return get_all_bots(app).get(bot_type)

def get_all_bots(app: FastAPI):
    if not hasattr(app.state, 'configured_bots'):
        app.state.configured_bots = get_configured_bots()
    return app.state.configured_bots