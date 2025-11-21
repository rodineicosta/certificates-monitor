import os
from dotenv import load_dotenv

load_dotenv()

SSH_CONFIG = {
    'hostname': os.getenv('SSH_HOST'),
    'port': int(os.getenv('SSH_PORT', 22)),
    'username': os.getenv('SSH_USERNAME'),
    'password': os.getenv('SSH_PASSWORD'),
}

DB_CONFIG = {
    'host': 'localhost',
    'port': int(os.getenv('DB_PORT', 3306)),
    'username': os.getenv('DB_USERNAME'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_DATABASE')
}