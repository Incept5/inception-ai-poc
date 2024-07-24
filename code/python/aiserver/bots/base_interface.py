from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseInterface(ABC):
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