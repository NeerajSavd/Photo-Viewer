import os
import sqlite3

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