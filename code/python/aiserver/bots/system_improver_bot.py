from .base_system_improver_bot import BaseSystemImproverBot


class SystemImproverBot(BaseSystemImproverBot):
    def __init__(self):
        super().__init__(system_src='/system_src')

    @property
    def bot_type(self) -> str:
        return "system-improver-bot"

    @property
    def description(self) -> str:
        return "System Improver Bot - Answer questions about the system"