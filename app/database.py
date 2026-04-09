import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "campus.db")

os.makedirs(DATA_DIR, exist_ok=True)

def get_db():
    if not os.path.exists(DB_PATH):
        open(DB_PATH, 'w').close()  # Create the file if it doesn't exist
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn