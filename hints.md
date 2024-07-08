# General

You could be asked to improve any part of the system and you should do your best to do that.
Below are some hints that might be helpful if you asked for a specific thing to do

## Bots

Bots are stored under code/python/aiserver/bots or a sub directory
When asked to add a new bot you should default to just adding a new file in the bots directory
If the bot is more complex and requires multiple files or a sub directory then you can create a new directory
The bot should be named after the file or directory name
If we are adding a bot remember to also add it to configured_bots.py
IMPORTANT: when creating a bot always extend langchain_bot_interface.py unless asked not to
IMPORTANT: when creating a bot look in simple_bot.py for a basic example of the pattern to follow
