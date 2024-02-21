#!/usr/bin/env bash
ps aux | grep main.py | awk '{print $2}' | xargs kill -9 2>/dev/null
python main.py &