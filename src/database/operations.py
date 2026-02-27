import os
import sqlite3

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