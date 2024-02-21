# telegram-bot
Telegram bot project to load to a server and launch. It starts a bot chat that with commands returns specific tasks output

## Pre-requisites
1. Create a .env file with the following variables:
```
# Telegram
BOT_TOKEN=your_bot_token
USER_ID=your_user_id

# Server
SERVER_LIST=your_server_list (comma separated) # e.g. server1,server2,server3

# Servers
SERVER1_SERVER_IP=your_server_ip
SERVER1_SERVER_PASSWORD=your_server_password
SERVER2_SERVER_IP=your_server_ip
SERVER2_SERVER_PASSWORD=your_server_password
SERVER3_SERVER_IP=your_server_ip
SERVER3_SERVER_PASSWORD=your_server_password
```

2. Create a virtual environment and install the requirements:
```
python3 -m venv .venv

# Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate

pip install -r requirements.txt
```

## Run the bot
```
./sync-bot.sh
```

### Check and close the process
```
ps aux | grep "python main.py"
kill -9 <pid>
```

## Usage
The bot needs to have the following commands:
```
# Check the status of the docker containers on dedicated servers
- /server

# Check the status of the docker containers on the local machine
- /docker
```
