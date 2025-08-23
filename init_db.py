import sqlite3

def save_log(action, host, params, status, output):
    conn = sqlite3.connect("nettools.db")
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO logs (action, host, params, status, output)
        VALUES (?, ?, ?, ?, ?)
    """, (action, host, str(params), status, output))
    conn.commit()
    conn.close()
