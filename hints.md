# General

You could be asked to improve any part of the system and you should do your best to do that.
Below are some hints that might be helpful if you asked for a specific thing to do

## requirements.txt
When generating new code and you use a package that is potentially new and you haven't
seen in use anywhere else then you should always fetch requirements.txt and add the package if necessary but prefer to use existing packages if possible.
If you have to add a new package then always inform the user with something like:
"WARNING: this update will require a docker-compose rebuild step to install the new package"
"From the ./docker directory run: docker-compose up --build"

## Bots

Bots are stored under code/python/aiserver/bots or a sub directory
When asked to add a new bot you should default to just adding a new file in the bots directory
If the bot is more complex and requires multiple files or a sub directory then you can create a new directory
The bot should be named after the file or directory name
If we are adding a bot remember to also add it to configured_bots.py
IMPORTANT: when creating a bot always find an example bot to copy and fetch the contents of that to use as a template first before generating any code 
Useful example template bots to use for inspiration include:
* code/python/aiserver/bots/simple_bot.py - default bot
* code/python/aiserver/bots/simple_rag_qa_bot.py for a RAG bot or if asked to use a retriever
IMPORTANT: when creating a method like def create_chatbot(self) don't forget to return the chatbot() function with return chatbot