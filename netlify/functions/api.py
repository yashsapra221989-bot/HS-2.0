import serverless_wsgi
import os
import sys

# Add the parent directory to sys.path so we can import app.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

def handler(event, context):
    """
    Netlify Function handler that adapts AWS Lambda events to WSGI (Flask).
    """
    return serverless_wsgi.handle_request(app, event, context)
