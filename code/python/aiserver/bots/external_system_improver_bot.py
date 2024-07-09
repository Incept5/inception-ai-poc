import os
from .base_system_improver_bot import BaseSystemImproverBot


class ExternalSystemImproverBot(BaseSystemImproverBot):
    def __init__(self):
        external_system_src = os.environ.get('EXTERNAL_SYSTEM_SRC', '/external_system_src')
        super().__init__(system_src=external_system_src)

    @property
    def bot_type(self) -> str:
        return "external-system-improver-bot"

    @property
    def description(self) -> str:
        return "External System Improver Bot - Answer questions about the configured external system"

    def create_chatbot(self):
        chatbot = super().create_chatbot()

        def wrapped_chatbot(state):
            result = chatbot(state)
            # Add a reminder about the external system source directory
            result["messages"][0].content += "\nIMPORTANT: All file paths should be relative to the external system source directory, which is mounted at /external_system_src."
            return result

        return wrapped_chatbot