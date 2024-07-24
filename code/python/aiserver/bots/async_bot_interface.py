from abc import abstractmethod
from typing import Dict, Any, AsyncGenerator
from bots.base_interface import BaseInterface


class AsyncBotInterface(BaseInterface):
    @abstractmethod
    async def process_request_async(self, user_input: str, context: str, **kwargs) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Process a user request asynchronously and return an async generator of responses.

        :param user_input: The user's input message
        :param context: Additional context for the conversation
        :param kwargs: Additional keyword arguments that might be needed for specific bot implementations
        :return: An async generator of response dictionaries
        """
        pass

    @abstractmethod
    async def process_request_async_final_only(self, user_input: str, context: str, **kwargs) -> str:
        """
        Process the request asynchronously and return only the final response as a string.

        :param user_input: The user's input query
        :param context: The context for the query
        :param kwargs: Additional keyword arguments
        :return: The final response as a string
        """
        pass