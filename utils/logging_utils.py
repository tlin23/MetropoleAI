import sqlite3
from datetime import datetime
import logging
import os
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db_path():
    """
    Get the database path from the environment variable or use the default.
    
    Returns:
        str: The database path
    """
    return os.environ.get("DB_PATH", "chat_logs.db")

def init_db():
    """
    Initialize SQLite database for logging chat interactions.
    Creates a table called chat_logs if it doesn't exist.
    """
    try:
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if the table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='chat_logs'")
        table_exists = cursor.fetchone() is not None
        
        if not table_exists:
            # Create new table with all columns
            cursor.execute('''
            CREATE TABLE chat_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                question TEXT,
                response TEXT,
                score REAL,
                response_type TEXT,
                raw_passages TEXT,
                filtered_out TEXT
            )
            ''')
        else:
            # Check if we need to add the new columns
            cursor.execute("PRAGMA table_info(chat_logs)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'score' not in columns:
                cursor.execute('ALTER TABLE chat_logs ADD COLUMN score REAL')
            
            if 'response_type' not in columns:
                cursor.execute('ALTER TABLE chat_logs ADD COLUMN response_type TEXT')
            
            if 'raw_passages' not in columns:
                cursor.execute('ALTER TABLE chat_logs ADD COLUMN raw_passages TEXT')
            
            if 'filtered_out' not in columns:
                cursor.execute('ALTER TABLE chat_logs ADD COLUMN filtered_out TEXT')
        
        conn.commit()
        conn.close()
        logger.info("Chat logs database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing chat logs database: {e}")

def log_interaction(
    question: str, 
    response: str, 
    score: float = None, 
    response_type: str = None,
    raw_passages: str = None,
    filtered_out: str = None
):
    """
    Log a chat interaction to the SQLite database.
    
    Args:
        question: The user's question
        response: The system's response
        score: The similarity score of the retrieved passage (optional)
        response_type: The type of response (e.g., "rewrite", "fallback", "error") (optional)
        raw_passages: JSON-encoded string of retained passages (optional)
        filtered_out: JSON-encoded string of filtered-out passages (optional)
    """
    try:
        timestamp = datetime.now().isoformat()
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO chat_logs (timestamp, question, response, score, response_type, raw_passages, filtered_out) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (timestamp, question, response, score, response_type, raw_passages, filtered_out)
        )
        conn.commit()
        conn.close()
        logger.info(f"Logged interaction at {timestamp} with response_type={response_type}, score={score}")
    except Exception as e:
        logger.error(f"Error logging interaction: {e}")
