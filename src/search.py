from geopy.geocoders import Nominatim
import requests
import os
from dotenv import load_dotenv
from prompt import process_request
import json
from database import init_db, query_dates, query_tags, query_coordinates, on_this_day_search
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
    except:
        return None, None

def on_this_day():
    conn = init_db()
    # today = [12,25]
    today = datetime.now().strftime("%Y-%m-%d").split('-')
    images = on_this_day_search(conn, today[1], today[2])
    conn.close()
    return images

def query(user_query):
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

def search(user_query):
    try:
        search_json = query(user_query).replace("```json", '').replace("```", '').replace("\n", '').strip()
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
    image_paths.sort(key=lambda x: x[1] if x[1] else '9999-99-99', reverse=True)
    image_paths = [row[0] for row in image_paths]
    return image_paths

if __name__ == "__main__":
    user_query = "winter"
    # result = search(user_query)
    result = on_this_day()
    print(result)