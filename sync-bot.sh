#!/bin/bash

echo "Restarting main.py..."
ps aux | grep main.py | awk '{print $2}' | xargs kill -9 2>/dev/null
source .venv/bin/activate
# nohup python main.py > /dev/null 2>&1 & 
python main.py
echo "Bot restarted."