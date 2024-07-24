from fastapi import APIRouter, HTTPException, Request, FastAPI
from fastapi.responses import StreamingResponse
from bots.configured_bots import get_all_bots, get_bot
from utils.debug_utils import debug_print
from bots.sync_bot_interface import SyncBotInterface
from bots.async_bot_interface import AsyncBotInterface
from bots.simple_bot_interface import SimpleBotInterface
import json
import traceback
from typing import Any, Dict, AsyncGenerator

def create_bot_router(app: FastAPI):
    bot_router = APIRouter()

    async def process_sync_bot(bot: SyncBotInterface, user_input: str, context: str, config: Dict[str, Any]) -> AsyncGenerator[str, None]:
        debug_print(f"*** Processing request synchronously for bot {bot.bot_type}")
        for response in bot.process_request(user_input, context, **config):
            yield f"data: {json.dumps(response)}\n\n"

    async def process_async_bot(bot: AsyncBotInterface, user_input: str, context: str, config: Dict[str, Any]) -> AsyncGenerator[str, None]:
        debug_print(f"*** Processing request asynchronously for bot {bot.bot_type}")
        async for response in bot.process_request_async(user_input, context, **config):
            yield f"data: {json.dumps(response)}\n\n"

    async def process_simple_bot(bot: SimpleBotInterface, user_input: str, context: str, config: Dict[str, Any]) -> AsyncGenerator[str, None]:
        debug_print(f"*** Processing simple request for bot {bot.bot_type}")
        response = bot.simple_process_request(user_input, context, **config)
        yield f"data: {json.dumps({'type': 'text', 'content': response})}\n\n"

    bot_processors = {
        AsyncBotInterface: process_async_bot,
        SyncBotInterface: process_sync_bot,
        SimpleBotInterface: process_simple_bot,
    }

    @bot_router.get('/bots')
    async def get_available_bots():
        """
        Returns a list of available bots with their descriptions and config options for the UI.
        Excludes system bots from the list.
        """
        configured_bots = get_all_bots(app)
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

        bot = get_bot(app, bot_type)
        if bot is None:
            debug_print(f"Error: Invalid bot type {bot_type}")
            raise HTTPException(status_code=400, detail=f"Invalid bot type {bot_type}")

        async def generate():
            try:
                for bot_interface, processor in bot_processors.items():
                    if isinstance(bot, bot_interface):
                        async for response in processor(bot, user_input, context, config):
                            yield response
                        break
                else:
                    raise ValueError(f"Unsupported bot type: {type(bot)}")
            except Exception as e:
                error_message = f"Error processing request: {str(e)}"
                stack_trace = traceback.format_exc()
                debug_print(f"{error_message}\n{stack_trace}")
                yield f"data: {json.dumps({'type': 'error', 'content': error_message})}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(generate(), media_type='text/event-stream')

    return bot_router