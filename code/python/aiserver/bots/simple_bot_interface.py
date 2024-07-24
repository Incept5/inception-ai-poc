from abc import ABC, abstractmethod
from typing import Dict, Any
from bots.base_interface import BaseInterface

class SimpleBotInterface(BaseInterface):
    @abstractmethod
    async def simple_process_request(self, user_input: str, context: str, **kwargs) -> str:
        """
        Process a user request asynchronously and return a response.

        :param user_input: The user's input message
        :param context: Additional context for the conversation
        :param kwargs: Additional keyword arguments that might be needed for specific bot implementations
        :return: The bot's response
        """
        pass