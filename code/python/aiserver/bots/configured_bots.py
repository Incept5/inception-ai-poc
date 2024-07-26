from collections import OrderedDict
from fastapi import FastAPI
from bots.simple_bot import SimpleBot
from bots.web_search_bot import WebSearchBot
from bots.ollama_bot import OllamaBot
from bots.system_improver_bot import SystemImproverBot
from bots.chart_generation_bot import ChartGenerationBot
from bots.web_app_bot import WebAppBot
from bots.simple_retriever_bot import SimpleRetrieverBot
from bots.iso20022_expert_bot import ISO20022ExpertBot
from bots.collaboration_agent_bot import CollaborationAgentBot
from bots.supervisor_agent_bot import SupervisorAgentBot
from bots.fast_mlx_bot import FastMlxBot
from bots.simple_db_bot import SimpleDBBot
from bots.webscraping_bot import WebScrapingBot
from bots.webscraping_db_bot import WebScrapingDBBot

def get_bot_factories():
    return OrderedDict([
        ("system-improver-bot", SystemImproverBot),
        ("web-app-bot", WebAppBot),
        ("simple-bot", SimpleBot),
        ("web-search-bot", WebSearchBot),
        ("ollama-bot", OllamaBot),
        ("simple-retriever-bot", SimpleRetrieverBot),
        ("chart-generation-bot", ChartGenerationBot),
        ("iso20022-expert-bot", ISO20022ExpertBot),
        #("collaboration-agent-bot", CollaborationAgentBot),
        #("supervisor-agent-bot", SupervisorAgentBot),
        ("fast-mlx-bot", FastMlxBot),
        ("simple-db-bot", SimpleDBBot),
        ("webscraping-bot", WebScrapingBot),
        ("webscraping-db-bot", WebScrapingDBBot),
        ("webscraping-engineer-bot", WebScrapingEngineerBot)
    ])

def get_bot(app: FastAPI, bot_type: str, thread_id: str):
    bot_factories = get_bot_factories()
    if bot_type not in bot_factories:
        return None
    
    if not hasattr(app.state, 'bot_instances'):
        app.state.bot_instances = {}
    
    if thread_id not in app.state.bot_instances:
        app.state.bot_instances[thread_id] = {}
    
    if bot_type not in app.state.bot_instances[thread_id]:
        app.state.bot_instances[thread_id][bot_type] = bot_factories[bot_type]()
    
    return app.state.bot_instances[thread_id][bot_type]

def get_all_bots(app: FastAPI):
    return get_bot_factories()
from .webscraping_engineer_bot import WebScrapingEngineerBot
