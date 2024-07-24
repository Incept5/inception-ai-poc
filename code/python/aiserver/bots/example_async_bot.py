from bots.async_bot_interface import AsyncBotInterface
import asyncio

class ExampleAsyncBot(AsyncBotInterface):
    @property
    def bot_type(self) -> str:
        return "example_async_bot"

    @property
    def description(self) -> str:
        return "An example asynchronous bot"

    def get_config_options(self):
        return {}

    async def process_request_async(self, user_input: str, context: str, **kwargs):
        yield {"type": "intermediate", "content": "Processing..."}
        await asyncio.sleep(1)  # Simulate some async work
        yield {"type": "final", "content": f"Async bot response to: {user_input}"}

    async def process_request_async_final_only(self, user_input: str, context: str, **kwargs) -> str:
        await asyncio.sleep(1)  # Simulate some async work
        return f"Async bot final response to: {user_input}"