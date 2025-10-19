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
    
    # Get port from environment variable (Railway sets this)
    port = int(os.environ.get('PORT', 5002))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    # Run the application
    app.run(
        debug=debug,
        host='0.0.0.0',
        port=port,
        threaded=True
    )
