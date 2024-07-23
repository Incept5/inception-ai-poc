from collections import OrderedDict
from fastapi import FastAPI
from bots.file_fixing_bot import FileFixingBot

class SystemBotManager:
    @staticmethod
    def initialize_system_bots(app: FastAPI):
        if not hasattr(app.state, 'system_bots'):
            system_bots = OrderedDict([
                ("file-fixing-bot", FileFixingBot()),
                # Add more system bots here as needed
            ])
            app.state.system_bots = system_bots

    @staticmethod
    def get_system_bot(app: FastAPI, bot_type: str):
        if not hasattr(app.state, 'system_bots'):
            SystemBotManager.initialize_system_bots(app)
        return app.state.system_bots.get(bot_type)

    @staticmethod
    def get_all_system_bots(app: FastAPI):
        if not hasattr(app.state, 'system_bots'):
            SystemBotManager.initialize_system_bots(app)
        return app.state.system_bots

# Dependency function for FastAPI
def get_system_bot_dependency(app: FastAPI):
    def _get_system_bot(bot_type: str):
        return SystemBotManager.get_system_bot(app, bot_type)
    return _get_system_bot