import paramiko
from decouple import config

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ConversationHandler

def connect_server(server_name, server_ip, password):
    # Create an SSH client
    ssh = paramiko.SSHClient()
    
    # Automatically add the server's host key
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    # Connect to the server
    # print(f"Connecting to the server {server_name}...")
    ssh.connect(server_ip, username='root', password=password)
    # print(f"Connected to the server {server_name} \n")
    
    # Execute the command to check the status of docker
    stdin, stdout, stderr = ssh.exec_command("docker ps --format '{{.Names}}'")
    
    # Read the output of the command
    output = stdout.read().decode('utf-8')
    
    # Close the connection
    ssh.close()
    return output

def run_docker_command(server):

    server_ip = config(server.upper() + '_SERVER_IP')
    password = config(server.upper() + '_SERVER_PASSWORD')
        
    # Run the command
    output = connect_server(server, server_ip, password)
    return output

#############################
### python-telegram-bot code
#############################

async def check_docker_in_server(update: Update, context) -> int:
    
    servers = config('SERVER_LIST').split(',')
    
    inline_keyboard = [
        [InlineKeyboardButton(server, callback_data=f'server_{server}') for server in servers]
    ]
    
    await update.message.reply_text(
        "Welcome! Please select the server you want to connect to:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard),
    )
    return ConversationHandler.END
