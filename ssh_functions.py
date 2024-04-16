import paramiko
from decouple import config

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler

def connect_server(server_ip: str, password: str, command: str) -> str:
    """
    Connect to a server using SSH and execute the command passed as an argument.
    
    The output of the command is returned as the last 4000 characters of the output
    because the Telegram API has a limit of 4096 characters per message when printing the output to the user.
    
    Args:
    - server_ip: The IP address of the server. (str)
    - password: The password to connect to the server. (str)
    - command: The command to execute in the server. (str)
    
    Returns:
    - output: The output of the command executed in the server. (str)
    """

    # Create an SSH client
    ssh = paramiko.SSHClient()

    # Automatically add the server's host key
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Connect to the server
    ssh.connect(server_ip, username='root', password=password)

    # Execute the command to check the status of docker
    stdin, stdout, stderr = ssh.exec_command(command)

    # Read the output of the command
    output = stdout.read().decode('utf-8')
    # take the last 4096 characters of the output
    output = output[-4000:] if len(output) > 0 else stderr.read().decode('utf-8')[-4000:]
    # Close the connection
    ssh.close()
    return output

def run_docker_command(server: str, command="docker ps --format '{{.Names}}'") -> str:
    """
    Run a docker command in a server or in the local machine.
    
    If the server is NOT 'self', the function will find the IP address and password of the server
    from the environment variables and connect to the server using SSH.
    
    Args:
    - server: The server to connect to. (str)
    - command: The command to execute. (str)
    
    Returns:
    - output: The output of the command executed in the server. (str)
    """
    from functions import run_local_command

    if server == 'self':
        return run_local_command(command)        
    else:
        server_ip = config(server.upper() + '_SERVER_IP')
        password = config(server.upper() + '_SERVER_PASSWORD')

        # Run the command
        output = connect_server(server_ip, password, command)
        return output

async def check_docker_in_server(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Ask the user which server to connect to.
    
    The user will be presented with an inline keyboard with the list of servers to choose from.
    
    The result of this function is to end the conversation and print the inline keyboard. It is an int because
    the ConversationHandler expects a return value of type int.
    
    Args:
    - update: The update object from the Telegram API. (telegram.Update)
    - context: The context object from the Telegram API. (telegram.ext.Context)
    
    Returns:
    - ConversationHandler.END: The conversation ends here after printing the inline keyboard. (int)
    """
    
    servers = config('SERVER_LIST').split(',')
    
    inline_keyboard = [
        [InlineKeyboardButton(server, callback_data=f'server_{server}') for server in servers]
    ]
    
    await update.message.reply_text(
        "Welcome! Please select the server you want to connect to:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard),
    )
    return ConversationHandler.END
