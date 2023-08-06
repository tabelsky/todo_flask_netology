import os

POSTGRES_PASSWORD=os.getenv('POSTGRES_PASSWORD', 'secret')
POSTGRES_USER=os.getenv('POSTGRES_USER', 'todo')
POSTGRES_DB=os.getenv('POSTGRES_DB', 'todo')
POSTGRES_HOST=os.getenv('POSTGRES_HOST', '127.0.0.1')
POSTGRES_PORT=os.getenv('POSTGRES_PORT', '5431')