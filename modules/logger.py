import sqlite3
import time

def log_usage(user_query, ai_response):
    conn = sqlite3.connect('usage_logs.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS logs
                 (timestamp TEXT, user_query TEXT, ai_response TEXT)''')
    c.execute("INSERT INTO logs VALUES (?, ?, ?)",
              (time.strftime("%Y-%m-%d %H:%M:%S"), user_query, ai_response))
    conn.commit()
    conn.close()
