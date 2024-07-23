from mylangchain.base_bot import BaseBot

class ExampleBaseBot(BaseBot):
    @property
    def bot_type(self) -> str:
        return "ExampleBaseBot"

    @property
    def description(self) -> str:
        return "An example bot that demonstrates the basic implementation of a BaseBot."

    def get_system_prompt(self) -> str:
        return "You are a helpful AI and will answer questions to the best of your ability. You are polite, friendly, and always strive to provide accurate and helpful information."


# This allows the bot to be easily imported and instantiated
def create_bot(default_llm_provider=None, default_llm_model=None):
    return ExampleBaseBot(default_llm_provider, default_llm_model)