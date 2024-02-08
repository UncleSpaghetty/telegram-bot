#!/usr/bin/env python
# pylint: disable=unused-argument
# This program is dedicated to the public domain under the CC0 license.

"""
This is a basic example of a Telegram bot that interacts with the user to run a Docker command.
The bot asks the user which server to connect to (rp or carrisiland) and then runs `docker ps`.
"""

import logging
import subprocess
import paramiko
from decouple import config
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, ConversationHandler, CallbackQueryHandler, ContextTypes, MessageHandler

TOKEN = config('BOT_TOKEN')

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Define states for the conversation
SELECT_SERVER, RUN_DOCKER_PS = range(2)

# Map server names to Docker command prefixes
SERVER_COMMANDS = {"rp": "docker ps", "carrisiland": "docker ps"}

# Connect server via ssh
def connect_server(server_name, server_ip, password):
    # Create an SSH client
    ssh = paramiko.SSHClient()
    # Automatically add the server's host key
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # Connect to the server
    print(f"Connecting to the server {server_name}...")
    ssh.connect(server_ip, username='root', password=password)
    print(f"Connected to the server {server_name} \n")
    # Execute the command to check the status of docker
    stdin, stdout, stderr = ssh.exec_command("docker ps --format '{{.Names}}'")
    # Read the output of the command
    output = stdout.read().decode('utf-8')
    # Close the connection
    ssh.close()
    return output

# Helper function to run Docker command
def run_docker_command(server):

    server_ip = ""
    password = ""
    
    # Match the selected server and set server_ip and password
    if server == "rp":
        server_ip = config('RP_SERVER_IP')
        password = config('RP_SERVER_PASSWORD')
    elif server == "carrisiland":
        server_ip = config('CARRISILAND_SERVER_IP')
        password = config('CARRISILAND_SERVER_PASSWORD')
    else:
        return "Invalid server. Please select rp or carrisiland."
    
    # Run the command
    output = connect_server(server, server_ip, password)
    return output

# Callback handler for inline keyboard buttons
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    data = query.data

    # Extract the server name from the callback data
    server = data.split('_')[-1]

    await query.message.reply_text(f"Connecting to {server} server...")

    # Run Docker command
    result = run_docker_command(server)

    await query.message.reply_text(f"Result of `docker ps` on {server} server:\n{result}")

    return ConversationHandler.END

async def start_docker(update: Update, context) -> int:
    inline_keyboard = [
        [InlineKeyboardButton("rp", callback_data='server_rp')],
        [InlineKeyboardButton("carrisiland", callback_data='server_carrisiland')]
    ]
    
    await update.message.reply_text(
        "Welcome! Please select the server you want to connect to:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard),
    )
    return SELECT_SERVER

# Cancel the conversation
async def cancel(update: Update, context) -> int:
    await update.message.reply_text("Conversation canceled.")
    return ConversationHandler.END

def main() -> None:
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).build()

    # Create the ConversationHandler with the states and handlers
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("docker", start_docker)],
        states={
            SELECT_SERVER: [],
            RUN_DOCKER_PS: [],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Add the ConversationHandler to the Application
    application.add_handler(conv_handler)
    
    # Add the callback handler for inline keyboard buttons
    application.add_handler(CallbackQueryHandler(button_click))
    
    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
