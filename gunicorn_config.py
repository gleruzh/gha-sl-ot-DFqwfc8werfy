import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

bind = '0.0.0.0:8000'
workers = 1
timeout = 120

def on_starting(server):
    load_dotenv()  # Ensure environment variables are loaded when Gunicorn starts
