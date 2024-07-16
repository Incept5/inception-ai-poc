from flask import current_app
from collections import OrderedDict
from bots.file_fixing_bot import FileFixingBot

class SystemBotManager:
    @staticmethod
    def initialize_system_bots():
        if 'system_bots' not in current_app.extensions:
            system_bots = OrderedDict([
                ("file-fixing-bot", FileFixingBot()),
                # Add more system bots here as needed
            ])
            current_app.extensions['system_bots'] = system_bots

    @staticmethod
    def get_system_bot(bot_type):
        if 'system_bots' not in current_app.extensions:
            SystemBotManager.initialize_system_bots()
        return current_app.extensions['system_bots'].get(bot_type)

    @staticmethod
    def get_all_system_bots():
        if 'system_bots' not in current_app.extensions:
            SystemBotManager.initialize_system_bots()
        return current_app.extensions['system_bots']