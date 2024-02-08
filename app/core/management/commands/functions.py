import subprocess

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler


async def start_docker(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Run docker ps command in this system
    output = subprocess.run(["docker", "ps", "--format", "'{{.Names}}'"], capture_output=True, text=True)
    await update.message.reply_text(f"Result of `docker ps` on this server:\n{output.stdout}")
    return ConversationHandler.END    


SERVER_COMMANDS = {"rp": "docker ps", "carrisiland": "docker ps"} #TODO: Add the actual commands for each server

# Callback handler for inline keyboard buttons
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    data = query.data

    # Extract the server name from the callback data
    item = data.split('_')[-1]
    if item in SERVER_COMMANDS:
        
        await query.message.reply_text(f"Connecting to {item} server...")
        
        # Run Docker command
        result = run_docker_command(item)

        await query.message.reply_text(f"Result of `docker ps` on {item} server:\n{result}")
        return ConversationHandler.END
    else:
        await query.message.reply_text("Invalid input. Please select a valid server.")
        return ConversationHandler.END
