import subprocess
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler

from ssh_functions import run_docker_command

async def start_docker(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Function called after the user sends the /docker command.
    
    The function will run the `docker ps` command and print the output in the chat.
    
    Args:
    - update: The update object from the Telegram API. (telegram.Update)
    - context: The context object from the Telegram API. (telegram.ext.Context)
    
    Returns:
    - ConversationHandler.END: The conversation ends here after printing the output. (int)
    """
    # Run docker ps command in this system
    output = subprocess.run("docker ps --format {{.Names}}", shell=True, capture_output=True, text=True)
    result = output.stdout[-4000:] if len(output.stdout) > 0 else output.stderr[-4000:]
    if len(result) == 0:
        result = "No containers are running."
    # save the output in the context
    context.user_data['selected_server'] = 'self'
    context.user_data['containers'] = result

    # using <pre> and <code> tags to format the output as code block
    await update.message.reply_text(f"<pre><code class='language-bash'>{result}</code></pre>",
                                    parse_mode="HTML")
    if len(output.stdout) == 0:
        await update.message.reply_text("No containers are running.")
        return ConversationHandler.END
    data = "docker"
    return await button(update, data, context)

def run_local_command(command: str ) -> str:
    """
    Called in `run_docker_command` function if the server is 'self'. Execute a command in the local machine.
    
    Args:
    - command: The command to execute. (str)
    
    Returns:
    - result: The output of the command executed in the local machine. (str)
    """
    # Run the command
    output = subprocess.run(command, shell=True, capture_output=True, text=True)
    result = output.stdout[-4000:] if len(output.stdout) > 0 else output.stderr[-4000:]
    return result


async def select_server_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Function called after the user selects a server from the inline keyboard.
    
    The function will check data from the inline keyboard.
    Based on the data, the function will run:
    - `docker ps` command in the selected server.
    - `docker logs` command if the user selects a container after selecting "Check container logs".
    - `docker errors` command if the user selects a container after selecting "Check container errors".
    - `docker stop` command if the user selects a container after selecting "Stop container".
    - `docker restart` command if the user selects a container after selecting "Restart docker-compose".
    - `docker network list` command if the user selects "Networks".
    - `docker network inspect` command if the user selects "Inspect network" after selecting a network.
    
    Args:
    - update: The update object from the Telegram API. (telegram.Update)
    - context: The context object from the Telegram API. (telegram.ext.Context)
    
    Returns:    
    - ConversationHandler.END: The conversation ends here after printing the output. (int)
    """

    # Get the data of the button pressed
    query = update.callback_query
    data = query.data
    
    # Get the selected server from the context
    selected_server = context.user_data.get('selected_server')

    match data:
        case "check_logs":
            context.user_data['command'] = "logs"
            return await button(query, data, context)
        
        case "check_errors":
            context.user_data['command'] = "errors"
            return await button(query, data, context)
        
        case "stop_containers":
            context.user_data['command'] = "stop"
            return await button(query, data, context)
        
        case "restart_docker_compose":
            context.user_data['command'] = "restart"
            return await button(query, data, context)

        case "network":
            context.user_data['command'] = "network list"
            loading_message = await query.message.reply_text(f"Running `network` on {selected_server} server...", parse_mode="markdown")
            
            # Get the list of networks to print in the chat
            result = run_docker_command(selected_server, "docker network list --format '{{.Name}} {{.Driver}} {{.Scope}}'")
            
            # Get the list of networks to use in the next step
            network_list = run_docker_command(selected_server, "docker network list --format '{{.Name}}'")
            context.user_data['networks_list'] = network_list
            
            await loading_message.edit_text(f"<pre><code class='language-bash'>{result}</code></pre>",
                                            parse_mode="HTML")
            await update.callback_query.answer()
            return await button(query, data, context)
        
        case "network_inspect":
            context.user_data['command'] = "network inspect"
            return await button(query, data, context)
        
        case "back":
            context.user_data['command'] = "back"
            return await button(query, data, context)
                
        # case a server is selected
        case _ if data.split('_')[0] == "server":
            context.user_data['command'] = "select_server"
            item = data.split('_')[1]
            await query.message.reply_text(f"Connecting to {item} server...", parse_mode="markdown")

            # Run Docker command (docker ps) in the selected server (item)
            result = run_docker_command(item)
            # update query context with the result
            context.user_data['selected_server'] = item
            context.user_data['containers'] = result

            await query.message.reply_text(f"<pre><code class='language-bash'>{result}</code></pre>",
                                            parse_mode="HTML")
            # await update.callback_query.answer() will remove the "loading" message after the output is successfully printed
            await update.callback_query.answer()
            return await button(query, data, context)

        #case a container is selected after selecting an action
        case _:
            # await update.callback_query.answer will propt a confirmation notification to the user
            # if the user pressed Ok to the notification the command will be executed
            # but calling await query.answer() will always return True
            # so wait for the user to press Ok to the notification
            command = context.user_data['command']
            
            if command == "stop" or command == "restart":
                if 'answer' not in context.user_data or context.user_data['answer'] != command:
                    await update.callback_query.answer('If you are sure you want to run this command, press Ok and select the container again.', show_alert=True)
                    context.user_data['answer'] = command
                    return ConversationHandler.END
            
            loading_message = await query.message.reply_text(f"Running `{command}` {data} on {selected_server} server...")
            
            # Run the selected command in the selected server
            # case restart docker-compose is selected, the command is different because it needs to get the container id,
            # the project working directory and then restart the docker-compose in the project working directory
            # case errors is selected, the command is different because it needs to run the docker logs command and then
            # grep the output for the word "error"
            match command:
                case "restart":
                    result = restart_docker_compose(selected_server, data)
                case "errors":
                    result = run_docker_command(selected_server, f"docker logs {data} 2>&1 | grep -i error")
                    if len(result) == 0:
                        result = "No errors found."
                case _:
                    result = run_docker_command(selected_server, f"docker {command} {data}")
            await loading_message.edit_text(f"<pre><code class='language-bash'>{result}</code></pre>",
                                            parse_mode="HTML")
            # await update.callback_query.answer() will remove the "loading" message after the output is successfully printed
            await update.callback_query.answer()
            return ConversationHandler.END
        
def restart_docker_compose(selected_server: str, data: str) -> int:
    """
    Restart docker-compose in the project working directory of the selected container.
    
    Args:
    - selected_server: The server to connect to. (str)
    - data: The container name. (str)
    
    Returns:
    - result: The output of the command executed in the server. (str)
    """
    get_container_id = run_docker_command(selected_server, f'docker ps -aqf name={data}')

    container_id = get_container_id.split('\n')[0]
    # format is literally -F\"
    format_option = '"'
    # get the project working directory of the container
    output = run_docker_command(selected_server, 
        f"docker inspect {container_id} | grep project.working_dir | awk -F\{format_option} '{{print $4}}'"
        )

    output = output.split('\n')[0]
    # restart docker-compose in the project working directory
    result = run_docker_command(selected_server, f"cd {output} && docker-compose restart")
    return result
    
def container_list(containers: list) -> list:
    """
    Split the list of containers into rows based on the maximum button width.
    
    Args:
    - containers: The list of containers. (list)
    
    Returns:
    - container_rows: The list of containers split into rows. (list)
    """
    # remove empty strings from the list
    containers = list(filter(None, containers))
    
    # Set maximum button width (adjust as needed)
    max_button_width = 40
    
    # Calculate the maximum length of container names
    max_name_length = max(len(container) for container in containers)

    # Initialize variables
    total_buttons = len(containers)
    remaining_buttons = total_buttons
    buttons_per_row = min(2, total_buttons)  # default value

    # Iterate through possible button counts per row
    while buttons_per_row > 0:
        # Calculate the number of rows needed
        rows_needed = (total_buttons + buttons_per_row - 1) // buttons_per_row

        # Check if the total width fits within the maximum button width
        total_width = buttons_per_row * max_name_length
        if total_width <= max_button_width * buttons_per_row:
            break  # found a valid arrangement
        
        buttons_per_row -= 1  # decrease buttons_per_row and try again

    # Ensure buttons_per_row is at least 1 to avoid range() error
    buttons_per_row = max(1, buttons_per_row)

    # Split containers into rows based on the calculated buttons_per_row
    container_rows = [containers[i:i + buttons_per_row] for i in range(0, total_buttons, buttons_per_row)]
    
    return container_rows
    
async def button(update: Update, data: str, context) -> int:
    """
    Create and print the inline keyboard buttons based on the data received (server name, container name, or action)
    
    Main function to print the inline keyboard with the list of containers or networks.
    
    Args:
    - update: The update object from the Telegram API. (telegram.Update)
    - data: The data received from the inline keyboard. (str)
    - context: The context object from the Telegram API. (telegram.ext.Context)
    
    Returns:
    - ConversationHandler.END: The conversation ends here after printing the inline keyboard. (int)
    """
    
    # Get the list of containers from the context
    containers = context.user_data['containers'].split('\n')
    
    # Split the list of containers into rows
    container_rows = container_list(containers)

    match data:
        # case the user selects "Check container logs", "Check container errors", "Stop container", or "Restart docker-compose"
        # the inline keyboard will have the list of containers with the back button
        case "check_logs" | "check_errors" | "stop_containers" | "restart_docker_compose":
            keyboard = [
                [InlineKeyboardButton(container, callback_data=container) for container in container_chunk]
                for container_chunk in container_rows
            ]
            keyboard.append([InlineKeyboardButton("Back", callback_data="back")])
        # case the user selects "Networks" and sees the list of networks or any action that lists
        # the containers, the inline keyboard will have the list of actions
        case "back":
            keyboard = [
                [InlineKeyboardButton("Check logs", callback_data='check_logs'),
                 InlineKeyboardButton("Stop container", callback_data='stop_containers'),
                 InlineKeyboardButton("Check errors", callback_data='check_errors')],
                [InlineKeyboardButton("Restart docker-compose", callback_data='restart_docker_compose')],
                [InlineKeyboardButton("Networks", callback_data='network')],
            ]
        # case the user selects a server or runs the /docker command, the inline keyboard will have the list of actions
        # to run in the server
        case _ if data.split('_')[0] == "server" or data == "docker":
            keyboard = [
                [InlineKeyboardButton("Check logs", callback_data='check_logs'),
                 InlineKeyboardButton("Stop container", callback_data='stop_containers'),
                 InlineKeyboardButton("Check errors", callback_data='check_errors')],
                [InlineKeyboardButton("Restart docker-compose", callback_data='restart_docker_compose')],
                [InlineKeyboardButton("Networks", callback_data='network')],
            ]
            reply_markup=InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                text="Please select an action:",
                reply_markup=reply_markup,
            )
            return ConversationHandler.END
        
        # case the user selects "Networks", the chat will show the list of networks
        # and inline keyboard will have the list of actions to run in the network with the back button
        case "network":
            keyboard = [
                [InlineKeyboardButton("List networks", callback_data='network')],
                [InlineKeyboardButton("Inspect network", callback_data='network_inspect')],
                [InlineKeyboardButton("Back", callback_data="back")]
            ]
            reply_markup=InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                text="Please select an action:",
                reply_markup=reply_markup,
            )
            return ConversationHandler.END

        # case the user selects "Inspect network", the chat will show the list of networks
        # and inline keyboard will have the list of networks with the back button
        case "network_inspect":
            # Get the list of networks from the context
            networks_list = context.user_data['networks_list'].split('\n')
            # Split the list of networks into rows
            network_rows = container_list(networks_list)
                        
            keyboard = [
                [InlineKeyboardButton(network, callback_data=network) for network in network_chunk]
                for network_chunk in network_rows
            ]
            keyboard.append(   
                [InlineKeyboardButton("Back", callback_data="network")]
            )
            reply_markup=InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                text="Please select a network:",
                reply_markup=reply_markup,
            )
            await update.answer()
            return ConversationHandler.END
        
        # case the data is invalid
        case _:
            keyboard = []

    reply_markup=InlineKeyboardMarkup(keyboard)
    
    await update.message.edit_text(
        text="Please select a container:",
        reply_markup=reply_markup,
    )
    
    # await update.answer() will remove the "loading" message after the inline keyboard is printed
    # and after the user selects an action
    await update.answer()
    return ConversationHandler.END
