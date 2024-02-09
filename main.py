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

from functions import start_docker, button_click
from ssh_functions import connect_server, check_docker_in_server

TOKEN = config('BOT_TOKEN')

# Define states for the conversation
SELECT_SERVER, RUN_DOCKER_PS = range(2)


# Cancel the conversation
async def end(update: Update, context) -> int:
    await update.message.reply_text("Conversation ended.")
    return ConversationHandler.END

def main() -> None:
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).build()

    # Create the ConversationHandler with the states and handlers
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("server", check_docker_in_server),
            CommandHandler("docker", start_docker),
            ],
        states={
            SELECT_SERVER: [],
            RUN_DOCKER_PS: [],
        },
        fallbacks=[CommandHandler("cancel", end)],
    )

    # Add the ConversationHandler to the Application
    application.add_handler(conv_handler, 1)
    
    # Add the callback handler for inline keyboard buttons
    application.add_handler(CallbackQueryHandler(button_click), 2)
    
    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
