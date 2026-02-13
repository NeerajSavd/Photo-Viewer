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

def insert_image(conn, filepath, metadata):
    c = conn.cursor()
    c.execute("""
            INSERT OR IGNORE INTO images (filepath, timestamp, latitude, longitude, camera_model)
            VALUES (?, ?, ?, ?, ?)
        """, (filepath, metadata.get("timestamp"), metadata.get("latitude"), metadata.get("longitude"), metadata.get("camera_model")))
    conn.commit()

def insert_tags(conn, filepath, tags):
    c = conn.cursor()
    for tag in tags:
        tag = tag.lower()
        c.execute("""
                INSERT OR IGNORE INTO tags (id, tag)
                VALUES ((SELECT id FROM images WHERE filepath = ?), ?)
            """, (filepath, tag))
    conn.commit()

def check_image_exists(conn, filepath):
    c = conn.cursor()
    c.execute("SELECT 1 FROM images WHERE filepath = ?", (filepath,))
    return c.fetchone() is not None

def delete_images(conn):
    c = conn.cursor()
    c.execute("SELECT filepath FROM images")
    for row in c.fetchall():
        if not os.path.exists(row[0]):
            c.execute("DELETE FROM images WHERE filepath = ?", (row[0],))
    conn.commit()

def delete_folder(conn, folder_path):
    c = conn.cursor()
    c.execute("SELECT filepath FROM images WHERE filepath LIKE ?", (folder_path + "%",))
    c.execute("DELETE FROM images WHERE filepath LIKE ?", (folder_path + "%",))
    print(f"Deleted {len(c.fetchall())} images from folder: {folder_path}")
    conn.commit()

# Query Functions

def query_dates(conn, dateStart = None, dateEnd = None):
    c = conn.cursor()
    c.execute("""SELECT filepath, timestamp FROM images WHERE (timestamp BETWEEN ? AND ?)""", (dateStart, dateEnd))
    return c.fetchall()

def on_this_day_search(conn, month, day):
    c = conn.cursor()
    images = []
    for y in range(2100, 2000, -1):
        c.execute("""SELECT filepath FROM images WHERE timestamp = ?""", (f"{y}-{month}-{day}",))
        rows = c.fetchall()
        if rows:
            images.append([y, []])
            for row in rows:
                images[-1][1].append(row[0])
    return images

def query_coordinates(conn, latMin, latMax, lonMin, lonMax):
    c = conn.cursor()
    c.execute("""
            SELECT filepath, timestamp FROM images
            WHERE (latitude BETWEEN ? AND ?) AND (longitude BETWEEN ? AND ?)
        """, (latMin, latMax, lonMin, lonMax))
    return c.fetchall()

def query_tags(conn, tags):
    c = conn.cursor()
    if type(tags) is str:
        c.execute("""
                SELECT images.filepath, images.timestamp FROM images
                JOIN tags ON images.id = tags.id
                WHERE tags.tag = ?
            """, (tags,))
    else:
        # For multiple tags, find images that have all the specified tags
        placeholders = ','.join('?' for _ in tags)
        c.execute(f"""
                SELECT images.filepath, images.timestamp FROM images
                JOIN tags ON images.id = tags.id
                WHERE tags.tag IN ({placeholders})
                GROUP BY images.id
                HAVING COUNT(DISTINCT tags.tag) = ?
            """, (*tags, len(tags)))
    return c.fetchall()

def get_metadata(conn, image_path):
    c = conn.cursor()
    c.execute("""
            SELECT images.timestamp, images.latitude, images.longitude, images.camera_model, tags.tag FROM tags
            JOIN images ON tags.id = images.id
            WHERE images.filepath = ?
        """, (image_path,))
    metadata = c.fetchall()
    details = {}
    for row in metadata:
        if len(details) == 0:
            details["timestamp"] = row[0]
            details["latitude"] = row[1]
            details["longitude"] = row[2]
            details["camera_model"] = row[3]
            details["tags"] = [row[4]]
        else:
            details["tags"].append(row[4])
    return details

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