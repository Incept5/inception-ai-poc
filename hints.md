# General

You could be asked to improve any part of the system and you should do your best to do that.
Below are some hints that might be helpful if you asked for a specific thing to do

## requirements.txt
* Before generating new code fetch the requirements.txt so you know what packages are already installed
* Always try very hard to limit your changes to the packages already defined in requirements.txt
* If you do have to add a new package to requirements.txt then always inform the user with something like:
"WARNING: this update will require a docker-compose rebuild step to install the new package"
"From the ./docker directory run: docker-compose up --build"

## Imports
Here is a list of preferred imports:

* from langchain_huggingface import HuggingFaceEmbeddings (not from from langchain.embeddings)
* from langchain_community.document_loaders import WikipediaLoader (not from langchain.document_loaders import WikipediaLoader)

## Bots

* Bots are stored under code/python/aiserver/bots or a sub directory
* When asked to add a new bot you should default to just adding a new file in the bots directory
* If the bot is more complex and requires multiple files or a sub directory then you can create a new directory
* The bot should be named after the file or directory name
* If we are adding a bot remember to also add it to configured_bots.py
* IMPORTANT: when creating a bot always find an example bot to copy and fetch the contents of that to use as a template first before generating any code 
* Useful example template bots to use for inspiration include:
  * code/python/aiserver/bots/simple_bot.py - default bot
  * code/python/aiserver/bots/simple_retriever_bot.py for a bot that needs to use a retriever
* IMPORTANT: when creating a method like def create_chatbot(self) don't forget to return the chatbot() function with return chatbot

## BotUI
When asked to make changes to the BotUI you should look in code/vue/botui for the relevant files
Always load the following files when asked about look and feel or styling issues:
* code/vue/botui/src/base.css
* code/vue/botui/src/global.css
* code/vue/botui/src/main.css

VERY IMPORTANT: Do not try to change ANY files under /code/web/botui as these are generated from the source files in code/vue/botui - fetch the source files and suggest edits to those files instead!

## test-system
When making changes to the test-system you should look under /code/test-system and bare these things in mind:
* The gradle build file is located at code/test-system/build.gradle.kts
* We are using yaml for application configuration in code/test-system/src/main/resources/application.yml