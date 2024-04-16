#!/bin/bash

echo "Installing dependencies..."
source .venv/bin/activate;
pip install --no-cache-dir -r requirements.txt;
echo "Dependencies installed successfully."
