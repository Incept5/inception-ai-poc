from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from bots.configured_bots import get_configured_bots, get_bot
from utils.debug_utils import debug_print
from bots.bot_interface import SimpleBotInterface
from mylangchain.langchain_bot_interface import LangchainBotInterface
import json
import traceback

bot_router = APIRouter()

@bot_router.get('/bots')
async def get_available_bots():
    """
    Returns a list of available bots with their descriptions and config options for the UI.
    Excludes system bots from the list.
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
    return available_bots

@bot_router.post('/bots/{bot_type}')
async def chat(bot_type: str, request: Request):
    debug_print(f"Received POST request to /bots/{bot_type}")
    data = await request.json()
    debug_print(f"Request data: {data}")

    user_input = data.get('message')
    context = data.get('context', '')
    config = data.get('config', {})

    if not user_input:
        debug_print("Error: No message provided")
        raise HTTPException(status_code=400, detail="No message provided")

    bot = get_bot(bot_type)
    if bot is None:
        debug_print(f"Error: Invalid bot type {bot_type}")
        raise HTTPException(status_code=400, detail=f"Invalid bot type {bot_type}")

    async def generate():
        try:
            if isinstance(bot, LangchainBotInterface):
                for response in bot.process_request(user_input, context, **config):
                    yield f"data: {json.dumps(response)}\n\n"
            elif isinstance(bot, SimpleBotInterface):
                response = bot.simple_process_request(user_input, context, **config)
                yield f"data: {json.dumps({'type': 'final', 'content': response})}\n\n"
            else:
                raise ValueError(f"Unsupported bot type: {type(bot)}")
        except Exception as e:
            error_message = f"Error processing request: {str(e)}"
            stack_trace = traceback.format_exc()
            debug_print(f"{error_message}\n{stack_trace}")
            yield f"data: {json.dumps({'type': 'error', 'content': error_message})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type='text/event-stream')