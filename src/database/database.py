import os
import sqlite3
from dotenv import load_dotenv
load_dotenv()
db_path = os.getenv("DB_PATH")

def init_db():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS images (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filepath TEXT UNIQUE,
        timestamp TEXT,
        latitude REAL,
        longitude REAL,
        camera_model TEXT
    );
    """)
    c.executescript("""
        CREATE TABLE IF NOT EXISTS tags (
        id INTEGER,
        tag TEXT,
        FOREIGN KEY (id) REFERENCES images(id),
        PRIMARY KEY (id, tag)
        );
    """)
    conn.commit()
    return conn

def debug_print_database(db_path):
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        table = 'images'

        print(f"\n--- Table: {table.upper()} ---")
        cursor.execute(f"SELECT * FROM {table}")
        rows = cursor.fetchall()
        headers = rows[0].keys()
        print(" | ".join(headers))
        print("-" * (len(" | ".join(headers)) + 2))
        for row in rows[-20:]:
            print(" | ".join(str(row[column]) for column in headers))
        
        cursor.execute("""SELECT COUNT(*) FROM images""")
        rows = cursor.fetchall()
        print("Total images:", rows[0][0])

        cursor.execute("""
            SELECT tags.tag, COUNT(tags.tag) AS count FROM tags
            GROUP BY tags.tag ORDER BY count DESC LIMIT 10
        """)
        rows = cursor.fetchall()
        print("\n--- Top Tags ---")
        for row in rows:
            print(" | ".join(str(value) for value in row))

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    debug_print_database(db_path)
    conn = init_db()
    # print(query_dates(conn, "2025-10-01", "2025-10-11"))
    # print(query_tags(conn, tags=["person", "outdoor"]))
    # delete_folder(conn, "E:\\OneDrive\\Pictures\\Camera Roll\\2020\\04")
    # delete_images(conn)
    # print(on_this_day_search(conn, "02", "02"))
    c = conn.cursor()
    conn.close()