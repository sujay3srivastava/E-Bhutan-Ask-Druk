# wsgi.py for Ask Druk - Bhutan's AI Citizen Assistant
import os
import sys
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Import the FastAPI application
from application import app

# WSGI application object that Elastic Beanstalk will use
application = app

# For debugging - print environment info
if __name__ == "__main__":
    print(f"Python path: {sys.path}")
    print(f"Current directory: {current_dir}")
    print(f"Application object: {application}")
    print("Starting application...")
    import uvicorn
    uvicorn.run(application, host="0.0.0.0", port=8000)
