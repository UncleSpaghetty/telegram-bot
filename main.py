#!/usr/bin/env python
# pylint: disable=unused-argument
# This program is dedicated to the public domain under the CC0 license.

"""
This is a basic example of a Telegram bot that interacts with the user to run a Docker command.
The bot asks the user which server to connect to and then runs `docker ps`.
"""

from decouple import config
from telegram import Update
from telegram.ext import Application, CommandHandler, ConversationHandler, CallbackQueryHandler

from functions import start_docker, select_server_button
from ssh_functions import check_docker_in_server

TOKEN = config('BOT_TOKEN')

# Define states for the conversation
SELECT_SERVER, RUN_DOCKER_PS, CHECK_LOGS = range(3)

def main() -> None:
    """
    Create the bot and start the conversation handler.
    
    The conversation handler is a state machine that will keep track of the user's input and
    guide the conversation to the next step.
    Entry points are the commands that the bot will listen to.
    
    `select_server_button` has been added as a callback handler for inline keyboard buttons.
    Each handler has a priority, which is used to determine the order in which the handlers are called.
    1. First the conversation handler is called, to set the enviroment of the bot (server or where the script is running).
    2. Then the callback handler is called to process the inline keyboard buttons.
    """
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).build()

    # Create the ConversationHandler with the states and handlers
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("docker", start_docker),
            CommandHandler("server", check_docker_in_server),
            ],
        states={
            RUN_DOCKER_PS: [],
            SELECT_SERVER: [],
            CHECK_LOGS: [],
        },
        fallbacks=[],
    )

    # Add the ConversationHandler to the Application
    application.add_handler(conv_handler, 1)
    
    # Add the callback handler for inline keyboard buttons
    application.add_handler(CallbackQueryHandler(select_server_button), 2)
    
    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
