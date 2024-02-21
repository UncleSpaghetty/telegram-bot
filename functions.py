import subprocess
from decouple import config
from telegram import Bot, Update, InlineKeyboardMarkup, InlineKeyboardButton
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

async def select_server_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    from main import SELECT_SERVER, CHECK_LOGS

    query = update.callback_query
    data = query.data

    match data:
        case "check_logs":
            context.user_data['command'] = "check_logs"
            return await button(query, context)

        case "drop_containers":
            context.user_data['command'] = "drop_containers"
            return await query.message.reply_text("Command not implemented yet.")                
        
        case "back":
            return await button(query, context)
        
        case _ if data.split('_')[0] == "server":
            context.user_data['command'] = "select_server"
            item = data.split('_')[1]
            if item in config('SERVER_LIST').split(','):
                await query.message.reply_text(f"Connecting to {item} server...")

                # Run Docker command
                result = run_docker_command(item)
                # update query context with the result
                context.user_data['selected_server'] = item
                context.user_data['containers'] = result

                await query.message.reply_text(f"Result of `docker ps` on {item} server:\n{result}")
                return await button(query, context)
            else:
                await query.message.reply_text("Invalid input. Please select a valid server.")
                return SELECT_SERVER

        #case containers
        case  _:
            if context.user_data.get('containers'):
                containers = context.user_data.get('containers').split('\n')
                containers = list(filter(None, containers))
                if data in containers:
                    context.user_data['command'] = "check_logs"
                    return await check_logs(update, context)
            else:
                await query.message.reply_text("Invalid input. Please select a valid server.")
                return SELECT_SERVER


async def check_logs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    from main import CHECK_LOGS
    selected_server = context.user_data.get('selected_server')

    if selected_server:
        try:
            if context.user_data.get('containers'):
                ### Run this if to check empty results from docker ps -> ['']
                ### else the restult is a string
                containers = context.user_data.get('containers').remove("") if context.user_data.get('containers') == [''] else context.user_data.get('containers')
                if containers:
                    containers = context.user_data.get('containers').split('\n')
                else:
                    containers = []
            else:
                containers = []

            query = update.callback_query
            data = query.data if query else None

            # user_container = update.message.text if update.message else None
            # user_container = user_container.lower() if user_container else None
            user_container = update.callback_query.data if update.callback_query else None
            
            if context.user_data.get('command') == "check_logs":
                command = True
            else:
                command = False

            if not command and user_container:
                await update.message.reply_text("Please select an action.")
                return ConversationHandler.END

            if command and not user_container:
                await query.message.reply_text("Please enter the log file name:")
                return CHECK_LOGS

            if command and user_container and len(containers) == 0:
                await update.message.reply_text("Can't check logs on no containers running. Select another server.")
                return ConversationHandler.END

            if command and user_container and user_container in containers:
                await query.message.reply_text(f"Running {user_container} logs on {selected_server}...")
                result = run_docker_command(selected_server, f"docker logs {user_container}")
                await query.message.reply_text(f"Result of `docker logs {user_container}` on {selected_server} server:\n{result}")

            return ConversationHandler.END
        except Exception as e:
            await query.message.reply_text(f"Error: {e}")
            return ConversationHandler.END
    else:
        await update.message.reply_text("Server not selected. Please select a server first.")
        return ConversationHandler.END

async def button(update: Update, context) -> int:
    containers = context.user_data['containers'].split('\n')
    # remove empty strings from the list
    containers = list(filter(None, containers))
    # split the list into chunks of 4
    containers = [containers[i:i + 4] for i in range(0, len(containers), 4)]

    match update.data:
        case "check_logs":
            keyboard = [
                [InlineKeyboardButton(container, callback_data=container) for container in containers[0]],
                [InlineKeyboardButton(container, callback_data=container) for container in containers[1]],
                [InlineKeyboardButton(container, callback_data=container) for container in containers[2]],
                [InlineKeyboardButton(container, callback_data=container) for container in containers[3]],
                [InlineKeyboardButton("Back", callback_data="back")]
            ]
        case "back":
            keyboard = [
                [InlineKeyboardButton("Check logs", callback_data='check_logs')],
                [InlineKeyboardButton("Drop containers", callback_data='drop_containers')],
            ]
        case _ if update.data.split('_')[0] == "server":
            keyboard = [
                [InlineKeyboardButton("Check logs", callback_data='check_logs')],
                [InlineKeyboardButton("Drop containers", callback_data='drop_containers')],
            ]
            reply_markup=InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                text="Please select a container:",
                reply_markup=reply_markup,
            )
                
            return ConversationHandler.END
        case _:
            keyboard = []

    reply_markup=InlineKeyboardMarkup(keyboard)
    
    await update.message.edit_text(
        text="Please select a container:",
        reply_markup=reply_markup,
    )
        
    return ConversationHandler.END