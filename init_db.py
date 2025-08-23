import sqlite3
from werkzeug.security import generate_password_hash

def create_db():
    conn = sqlite3.connect("nettools.db")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            action TEXT,
            host TEXT,
            params TEXT,
            status TEXT,
            output TEXT
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user'
        );
    """)
    conn.commit()
    conn.close()

def create_user(username, password, role="user"):
    create_db()
    conn = sqlite3.connect("nettools.db")
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (username, generate_password_hash(password, method="pbkdf2:sha256"), role)
        )
        conn.commit()
        conn.close()
    except sqlite3.IntegrityError:
        conn.close()

def save_log(action, host, params, status, output):
    create_db()
    conn = sqlite3.connect("nettools.db")
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO logs (action, host, params, status, output)
        VALUES (?, ?, ?, ?, ?)
    """, (action, host, str(params), status, output))
    conn.commit()
    conn.close()

def delete_logs():
    conn = sqlite3.connect("nettools.db")
    cur = conn.cursor()
    cur.execute("DELETE FROM logs")
    conn.commit()
    conn.close()

def delete_log(log_id):
    conn = sqlite3.connect("nettools.db")
    cur = conn.cursor()
    cur.execute("""
        DELETE FROM logs
        WHERE id = ?""", (log_id,))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_db()
