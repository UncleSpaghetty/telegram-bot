import subprocess
from decouple import config

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from ssh_functions import run_docker_command


async def start_docker(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Run docker ps command in this system
    output = subprocess.run(["docker", "ps", "--format", "'{{.Names}}'"], capture_output=True, text=True)
    await update.message.reply_text(f"Result of `docker ps` on this server:\n{output.stdout}")
    if len(output.stdout) == 0:
        await update.message.reply_text("No containers are running.")
    return ConversationHandler.END    


# Callback handler for inline keyboard buttons
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    data = query.data
    print(data)
    # Extract the server name from the callback data
    if data.split('_')[0] == "server":
        item = data.split('_')[1]
        if item in config('SERVER_LIST').split(','):
            
            await query.message.reply_text(f"Connecting to {item} server...")
            
            # Run Docker command
            result = run_docker_command(item)

            await query.message.reply_text(f"Result of `docker ps` on {item} server:\n{result}")
            return ConversationHandler.END
        else:
            await query.message.reply_text("Invalid input. Please select a valid server.")
            return ConversationHandler.END
    else:
        await query.message.reply_text("Invalid input. Please select a valid server.")
        return ConversationHandler.END
