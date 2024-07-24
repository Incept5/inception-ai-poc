from abc import abstractmethod
from typing import Dict, Any, Generator, Optional
from bots.base_interface import BaseInterface


class SyncBotInterface(BaseInterface):
    @abstractmethod
    def process_request(self, user_input: str, context: str, **kwargs) -> Generator[Dict[str, Any], None, None]:
        """
        Process a user request and return a generator of responses.

        :param user_input: The user's input message
        :param context: Additional context for the conversation
        :param kwargs: Additional keyword arguments that might be needed for specific bot implementations
        :return: A generator of response dictionaries
        """
        pass

    @abstractmethod
    def process_request_sync_final_only(self, user_input: str, context: str, **kwargs) -> str:
        """
        Process the request synchronously and return only the final response as a string.

        :param user_input: The user's input query
        :param context: The context for the query
        :param kwargs: Additional keyword arguments
        :return: The final response as a string
        """
        pass


class SimpleSyncBotInterface(SyncBotInterface):
    @abstractmethod
    def simple_process_request(self, user_input: str, context: str, **kwargs) -> str:
        """
        Process a user request and return a response.

        :param user_input: The user's input message
        :param context: Additional context for the conversation
        :param kwargs: Additional keyword arguments that might be needed for specific bot implementations
        :return: The bot's response
        """
        pass

    def process_request(self, user_input: str, context: str, **kwargs) -> Generator[Dict[str, Any], None, None]:
        response = self.simple_process_request(user_input, context, **kwargs)
        yield {"type": "final", "content": response}

    def process_request_sync_final_only(self, user_input: str, context: str, **kwargs) -> str:
        return self.simple_process_request(user_input, context, **kwargs)


class LangchainSyncBotInterface(SyncBotInterface):
    # Include relevant methods from the current LangchainBotInterface
    # Implement process_request and process_request_sync_final_only methods
    pass