#!/usr/bin/env python
"""
Run script for the Intelligent Hospital Information System (I-HIS).

This script starts the Flask development server.
"""
import os
from app import create_app

if __name__ == '__main__':
    # Get configuration environment
    env = os.environ.get('FLASK_ENV', 'development')
    
    # Create Flask app
    app = create_app(env)
    
    # Run the application
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=(env == 'development')
    )
