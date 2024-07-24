from bots.sync_bot_interface import SimpleSyncBotInterface

class ExampleSimpleBot(SimpleSyncBotInterface):
    @property
    def bot_type(self) -> str:
        return "example_simple_bot"

    @property
    def description(self) -> str:
        return "An example simple bot"

    def get_config_options(self):
        return {}

    def simple_process_request(self, user_input: str, context: str, **kwargs) -> str:
        return f"Simple bot response to: {user_input}"