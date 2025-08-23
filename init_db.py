import sqlite3

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
    );""")
    conn.commit()
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
