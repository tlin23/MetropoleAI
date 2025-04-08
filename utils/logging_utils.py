import sqlite3
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    """
    Initialize SQLite database for logging chat interactions.
    Creates a table called chat_logs if it doesn't exist.
    """
    try:
        conn = sqlite3.connect('chat_logs.db')
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            question TEXT,
            response TEXT
        )
        ''')
        conn.commit()
        conn.close()
        logger.info("Chat logs database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing chat logs database: {e}")

def log_interaction(question: str, response: str):
    """
    Log a chat interaction to the SQLite database.
    
    Args:
        question: The user's question
        response: The system's response
    """
    try:
        timestamp = datetime.now().isoformat()
        conn = sqlite3.connect('chat_logs.db')
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO chat_logs (timestamp, question, response) VALUES (?, ?, ?)',
            (timestamp, question, response)
        )
        conn.commit()
        conn.close()
        logger.info(f"Logged interaction at {timestamp}")
    except Exception as e:
        logger.error(f"Error logging interaction: {e}")
