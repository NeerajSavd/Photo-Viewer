import os

# Insertion 

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

# Deletion 

def clean_up_images(conn):
    c = conn.cursor()
    # Remove images with no metadata (timestamp, latitude, longitude, camera_model are all NULL)
    c.execute("""
        DELETE FROM images
        WHERE id IN (
            SELECT id FROM images
            WHERE timestamp IS 'Unknown'
        )
    """)
    # Remove images with no tags
    c.execute("""
        DELETE FROM images
        WHERE id NOT IN (SELECT DISTINCT id FROM tags)
    """)
    # Remove orphaned tags (tags referencing non-existent images)
    c.execute("""
        DELETE FROM tags
        WHERE id NOT IN (SELECT id FROM images)
    """)
    # Remove images that no longer exist
    c.execute("SELECT filepath FROM images")
    for row in c.fetchall():
        if not os.path.exists(row[0]):
            c.execute("DELETE FROM TAGS WHERE id = (SELECT id FROM images WHERE filepath = ?)", (row[0],))
            c.execute("DELETE FROM images WHERE filepath = ?", (row[0],))
    conn.commit()

def delete_image(conn, filepath):
    c = conn.cursor()
    c.execute("DELETE FROM tags WHERE id = (SELECT id FROM images WHERE filepath = ?)", (filepath,))
    c.execute("DELETE FROM images WHERE filepath = ?", (filepath,))
    conn.commit()

# Queries

def query_dates(conn, dateStart = None, dateEnd = None):
    c = conn.cursor()
    c.execute("""SELECT filepath, timestamp FROM images WHERE (timestamp BETWEEN ? AND ?)""", (dateStart, dateEnd))
    return c.fetchall()

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

def get_on_this_day(conn, month, day):
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

def get_locations(conn):
    cursor = conn.cursor()
    query = """
        SELECT latitude, longitude 
        FROM images 
        WHERE latitude IS NOT NULL AND longitude IS NOT NULL
    """
    cursor.execute(query)
    return cursor.fetchall()

def get_recent_images(conn, limit=50):
    c = conn.cursor()
    query = """
        SELECT filepath
        FROM images
        ORDER BY timestamp DESC
        LIMIT ?
    """
    c.execute(query, (limit,))
    return c.fetchall()

def get_total_image_stats(conn):
    output = {}
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM images")
    output["Total images"] = c.fetchone()[0]

    c.execute("""
        SELECT AVG(tag_count) as avg_tags
        FROM (
            SELECT COUNT(*) as tag_count
            FROM tags
            GROUP BY id
        )
    """)
    row = c.fetchone()
    output["Average tags per image"] = round(row[0], 2)

    c.execute("SELECT COUNT(DISTINCT tag) FROM tags")
    output["Unique tags"] = c.fetchone()[0]
    return output

def get_most_common_tags(conn, limit=10):
    c = conn.cursor()
    c.execute("""
        SELECT tags.tag, COUNT(*) as count
        FROM tags
        GROUP BY tags.tag
        ORDER BY count DESC
        LIMIT ?
    """, (limit,))
    return c.fetchall()

def get_images_per_year(conn):
    c = conn.cursor()
    c.execute("""
        SELECT strftime('%Y', timestamp) as year, COUNT(*) as count
        FROM images
        WHERE timestamp IS NOT NULL AND timestamp != 'Unknown'
        GROUP BY year
        ORDER BY year DESC
    """)
    return c.fetchall()

def get_images_per_camera(conn):
    c = conn.cursor()
    c.execute("""
        SELECT camera_model, COUNT(*) as count
        FROM images
        WHERE camera_model IS NOT NULL AND camera_model != 'Unknown'
        GROUP BY camera_model
        ORDER BY count DESC
    """)
    return c.fetchall()

if __name__ == "__main__":
    from database import init_db