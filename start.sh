#!/bin/bash
# Toyota Financial Services - Startup Script

echo "Starting Toyota Financial Services app..."
echo "Installing dependencies..."
pip3 install -r requirements.txt

echo "Starting Flask application..."
cd src
python3 app.py
