from abc import ABC, abstractmethod
from typing import Dict, Any


class BotInterface(ABC):
    @property
    @abstractmethod
    def bot_type(self) -> str:
        """Return the type of the bot."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Return a short description of the bot."""
        pass

    @abstractmethod
    def get_config_options(self) -> Dict[str, Any]:
        """
        Return a dictionary of configuration options specific to this bot.

        :return: A dictionary where keys are option names and values are option metadata
        (e.g., type, description, possible values)
        """
        pass


class SimpleBotInterface(BotInterface):
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