#!/usr/bin/env python3
"""
Toyota Financial Services - Smart Vehicle Financing
HackTX 2024 Entry

Run the Flask application
"""

import os
import sys
from dotenv import load_dotenv
from src.app import app

# Load environment variables from .env file
load_dotenv()

if __name__ == '__main__':
    # Add src directory to Python path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
    
    # Run the application
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5002,
        threaded=True
    )
