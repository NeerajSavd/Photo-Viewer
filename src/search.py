from geopy.geocoders import Nominatim
import requests
import os
from dotenv import load_dotenv
from prompt import process_request
import json
from database import init_db, query_dates, query_tags, query_coordinates, on_this_day_search, get_metadata
from datetime import datetime
import itertools
load_dotenv()

server_url = os.getenv("SEARCH_MODEL_URL")

def _get_coordinates(city):
    geolocator = Nominatim(user_agent="city_coords")
    try:
        location = geolocator.geocode(city)
        if location:
            return location.latitude, location.longitude
    except Exception as e:
        print(f"Error getting coordinates for '{city}': {e}")
        return None, None

def on_this_day():
    conn = init_db()
    # today = [12,25]
    today = datetime.now().strftime("%Y-%m-%d").split('-')
    images = on_this_day_search(conn, today[1], today[2])
    conn.close()
    return images

def _query(user_query):
    prompt = process_request(user_query)
    payload = {
        "model": "gemma",
        "messages": [{
            "role": "user",
            "content": prompt
        }],
        "max_tokens": 150,
        "temperature": 0.0
    }
    try:
        response = requests.post(server_url, json=payload)
        res_json = response.json()
        content = res_json['choices'][0]['message']['content']
        return content
    except Exception as e:
        return f"Error: {str(e)}"

def search_llm(user_query):
    try:
        search_json = _query(user_query).replace("```json", '').replace("```", '').replace("\n", '').strip()
        search_params = json.loads(search_json)
        print(f"Search parameters: {search_params}")
    except json.JSONDecodeError:
        return []
    
    conn = init_db()
    if 'date_range' in search_params and len(search_params['date_range']) == 2:
        dateStart = search_params['date_range'][0]
        dateEnd = search_params['date_range'][1]
        date_results = query_dates(conn, dateStart, dateEnd)
    
    if 'location' in search_params and search_params['location']:
        city = search_params['location']
        lat, lon = _get_coordinates(city)
        if lat is not None and lon is not None:
            latMin = lat - 0.5
            latMax = lat + 0.5
            lonMin = lon - 0.5
            lonMax = lon + 0.5
            location_results = query_coordinates(conn, latMin, latMax, lonMin, lonMax)
    
    if 'tags' in search_params and search_params['tags']:
        tags = search_params['tags']
        tag_results = []
        if type(tags[0]) is list:
            combinations = list(itertools.product(*tags))
            for combination in combinations:
                tag_results.extend(query_tags(conn, combination))
        else:
            for tag in tags:
                tag_results.extend(query_tags(conn, tag))
    
    conn.close()
    result_sets = []
    if 'date_range' in search_params and len(search_params['date_range']) == 2:
        result_sets.append(set([row for row in date_results]))
    if 'location' in search_params and search_params['location']:
        result_sets.append(set([row for row in location_results]))
    if 'tags' in search_params and search_params['tags']:
        result_sets.append(set([row for row in tag_results]))

    image_paths = []
    if result_sets:
        final_results = set.intersection(*result_sets)
        image_paths = list(final_results)
    image_paths.sort(key=lambda x: x[1] if (x[1] and x[1] != 'Unknown') else '0000-00-00', reverse=True)
    image_paths = [row[0] for row in image_paths]
    return image_paths

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

def get_image_details(image_path):
    conn = init_db()
    details = get_metadata(conn, image_path)
    conn.close()
    return details

if __name__ == "__main__":
    user_query = "winter"
    # result = search(user_query)
    # result = on_this_day()
    result = _get_coordinates("Seattle")
    print(result)
