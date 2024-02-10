import subprocess
from decouple import config

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from ssh_functions import run_docker_command


async def start_docker(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Run docker ps command in this system
    output = subprocess.run(["docker", "ps", "--format", "'{{.Names}}'"], capture_output=True, text=True)
    
    # save the output in the context
    context.user_data['selected_server'] = 'self'
    context.user_data['containers'] = output.stdout.split('\n')
    
    await update.message.reply_text(f"Result of `docker ps` on this server:\n{output.stdout}")
    if len(output.stdout) == 0:
        await update.message.reply_text("No containers are running.")
    return ConversationHandler.END    


# Callback handler for inline keyboard buttons
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    data = query.data

    # Extract the server name from the callback data
    if data.split('_')[0] == "server":
        item = data.split('_')[1]
        if item in config('SERVER_LIST').split(','):
            
            await query.message.reply_text(f"Connecting to {item} server...")
            
            # Run Docker command
            result = run_docker_command(item)
            # update query context with the result
            context.user_data['selected_server'] = item
            context.user_data['containers'] = result

            await query.message.reply_text(f"Result of `docker ps` on {item} server:\n{result}")
            await query.message.reply_text("Please enter the container name to check the logs.")
            return ConversationHandler.END
        else:
            await query.message.reply_text("Invalid input. Please select a valid server.")
            return ConversationHandler.END
    else:
        await query.message.reply_text("Invalid input. Please select a valid server.")
        return ConversationHandler.END

async def check_logs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Please enter the log file name:")
    
    containers = context.user_data.get('containers').split('\n') if context.user_data.get('containers') else []
    
    if update.message.text not in containers:
        await update.message.reply_text("Invalid input. Please enter a valid log file name.")
        return ConversationHandler.END

    # Retrieve the selected server from the conversation context
    selected_server = context.user_data.get('selected_server')

    if selected_server:
        if update.message.text and update.message.text in containers:
            log_file = update.message.text
            await update.message.reply_text(f"Running {log_file} logs on {selected_server}...")
            result = run_docker_command(selected_server, f"docker logs {log_file}")
            await update.message.reply_text(f"Result of `docker logs {log_file}` on {selected_server} server:\n{result}")

        return ConversationHandler.END
    else:
        await update.message.reply_text("Server not selected. Please select a server first.")
        return ConversationHandler.END
