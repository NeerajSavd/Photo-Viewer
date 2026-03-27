from geopy.geocoders import Nominatim
from database.database import init_db
from database.operations import *
from datetime import datetime
import math
from collections import defaultdict

def _get_coordinates(city):
    geolocator = Nominatim(user_agent="city_coords")
    try:
        location = geolocator.geocode(city)
        if location:
            return location.latitude, location.longitude
    except Exception as e:
        print(f"Error getting coordinates for '{city}': {e}")
        return None, None

def _parse_tags_with_operators(tags):
    if not tags:
        return []
    parts = tags.split()
    parsed = []
    current_group = []
    not_tags = []
    i = 0
    
    while i < len(parts):
        part = parts[i]
        if part.upper() == 'AND':
            pass
        elif part.upper() == 'OR':
            if current_group:
                parsed.append(current_group)
                current_group = []
        elif part.upper() == 'NOT':
            if current_group:
                parsed.append(current_group)
                current_group = []
            if i + 1 < len(parts):
                not_tag = parts[i + 1]
                not_tags.append(['NOT', not_tag])
                i += 1
        else:
            current_group.append(part)
        i += 1
    if current_group:
        parsed.append(current_group)
    # Append NOT tags at the end
    parsed.extend(not_tags)
    return parsed

def search(tags, location, dateStart, dateEnd):
    conn = init_db()

    if dateStart and dateEnd:
        date_results = query_dates(conn, dateStart, dateEnd)
    if location:
        print(f"Location: {location}")
        lat, lon = _get_coordinates(location)
        print(f"Coordinates: {lat}, {lon}")
        if lat is not None and lon is not None:
            latMin = lat - 0.5
            latMax = lat + 0.5
            lonMin = lon - 0.5
            lonMax = lon + 0.5
            location_results = query_coordinates(conn, latMin, latMax, lonMin, lonMax)
        else:
            location_results = []
    if tags:
        tag_results = []
        parsed_tags = _parse_tags_with_operators(tags)
        print(f"Parsed tags: {parsed_tags}")
        for group in parsed_tags:
            if not group:
                continue
            if group[0].upper() == 'NOT' and len(group) == 2:
                not_tag = group[1]
                not_results = query_tags(conn, [not_tag])
                tag_results = [r for r in tag_results if r not in not_results]
            else:
                group_results = []
                for tag in group:
                    tag_results_list = query_tags(conn, [tag])
                    if not group_results:
                        group_results = tag_results_list
                    else:
                        group_results = list(set(group_results) & set(tag_results_list))
                
                if group_results and len(group) > 1:
                    group_results = list(set(group_results))
                tag_results.extend(group_results)
    
    conn.close()
    result_sets = []
    if dateStart and dateEnd:
        result_sets.append(set([row for row in date_results]))
    if location:
        result_sets.append(set([row for row in location_results]))
    if tags:
        result_sets.append(set([row for row in tag_results]))

    image_paths = []
    if result_sets:
        final_results = set.intersection(*result_sets)
        image_paths = list(final_results)
    image_paths.sort(key=lambda x: x[1] if (x[1] and x[1] != 'Unknown') else '0000-00-00', reverse=True)
    image_paths = [row[0] for row in image_paths]
    return image_paths

def on_this_day(date: str = None):
    conn = init_db()
    if date is None:
        today = datetime.now().strftime("%Y-%m-%d").split('-')
    else:
        parts = date.split('/')
        today = [datetime.now().year, parts[0], parts[1]]
    images = get_on_this_day(conn, today[1], today[2])
    conn.close()
    return images

def recent_images():
    conn = init_db()
    images = get_recent_images(conn, 50)
    conn.close()
    return images

def image_details(image_path):
    conn = init_db()
    details = get_metadata(conn, image_path)
    conn.close()
    return details

def image_map():
    conn = init_db()
    rows = get_locations(conn)
    conn.close()

    # 1 degree of latitude is consistently ~69.1 miles anywhere on Earth.
    MILES_PER_LAT_DEGREE = 69.1
    GRID_SIZE_MILES = 20.0
    LAT_DEG_BIN_SIZE = GRID_SIZE_MILES / MILES_PER_LAT_DEGREE

    grid_counts = defaultdict(int)

    for lat, lon in rows:
        try:
            lat = float(lat)
            lon = float(lon)
        except ValueError:
            continue

        lat_bin = round(lat / LAT_DEG_BIN_SIZE)
        center_lat = lat_bin * LAT_DEG_BIN_SIZE

        cos_lat = math.cos(math.radians(center_lat))
        
        if cos_lat < 0.01: 
            lon_deg_bin_size = 360.0
        else:
            lon_deg_bin_size = GRID_SIZE_MILES / (MILES_PER_LAT_DEGREE * cos_lat)

        lon_bin = round(lon / lon_deg_bin_size)
        center_lon = lon_bin * lon_deg_bin_size

        grid_counts[(center_lat, center_lon)] += 1

    return [[lat, lon, count] for (lat, lon), count in grid_counts.items()]

def library_stats():
    conn = init_db()
    stats = {
        "total_images": get_total_image_stats(conn),
        "most_common_tags": get_most_common_tags(conn, 10),
        "images_per_year": get_images_per_year(conn),
        "images_per_camera": get_images_per_camera(conn),
    }
    conn.close()
    return stats

if __name__ == "__main__":
    user_query = "winter"
    # result = search(user_query)
    # result = on_this_day()
    result = _get_coordinates("Seattle")
    print(result)
