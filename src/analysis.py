import base64
import requests
import io
import os
from PIL import Image
from pillow_heif import register_heif_opener
import time
from PIL.ExifTags import TAGS, GPSTAGS
from geopy.geocoders import Nominatim
import re
from dotenv import load_dotenv
load_dotenv()

register_heif_opener()

server_url = os.getenv("VISION_MODEL_URL")
session = requests.Session()

def encode_image(img):
    img.thumbnail((336, 336))
    buffer = io.BytesIO()
    try:
        img.save(buffer, format="JPEG", quality=85)
    except OSError:
        img = img.convert("RGB")
        img.save(buffer, format="JPEG", quality=85)
    return base64.b64encode(buffer.getvalue()).decode('utf-8')

def query(img_path, prompt):
    # start_time = time.time()
    with Image.open(img_path) as img:
        base64_image = encode_image(img)
    # print(f"Image encoded in {time.time() - start_time:.2f} seconds.")
    # start_time = time.time()
    
    payload = {
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                }
            ]
        }],
        "max_tokens": 75,
        "temperature": 0.0
    }

    try:
        response = session.post(server_url, json=payload)
        res_json = response.json()
        # print(f"Server responded in {time.time() - start_time:.2f} seconds.")
        return res_json['choices'][0]['message']['content']
        # return res_json
    except Exception as e:
        raise Exception(f"Query failed for {img_path}: {str(e)}")

def _get_decimal_from_dms(dms, ref):
    degrees = dms[0]
    minutes = dms[1] / 60.0
    seconds = dms[2] / 3600.0
    
    if ref in ['S', 'W']:
        return -float(degrees + minutes + seconds)
    return float(degrees + minutes + seconds)

def get_metadata(image_path):
    with Image.open(image_path) as img:
        exif_data = img.getexif()
        if not exif_data:
            return {"timestamp": '', "camera_model": '', "latitude": '', "longitude": ''}
        
        timestamp, camera_model = '', ''
        if image_path.lower().endswith('.png'):
            createDate1 = r'xmp:CreateDate="(\d{4})-(\d{2})-(\d{2})T'
            createDate2 = r'<photoshop:DateCreated>(\d{4})-(\d{2})-(\d{2})'
            model = r'tiff:Model="([^"]+)"'
            for _, value in img.info.items():
                if isinstance(value, str):
                    timestamp = re.search(createDate1, value) or re.search(createDate2, value)
                    camera_model = re.search(model, value)
                    if timestamp:
                        timestamp = f"{timestamp.group(1)}-{timestamp.group(2)}-{timestamp.group(3)}"
                    if camera_model:
                        camera_model = camera_model.group(1)
        else:
            timestamp = exif_data.get(36867) or exif_data.get(306) or "Unknown"
            timestamp = timestamp.replace(':', '-', 2).split(' ')[0]
            camera_model = exif_data.get(272) or "Unknown"

        gps_info = {}
        for tag_id in exif_data:
            tag_name = TAGS.get(tag_id, tag_id)
            if tag_name == "GPSInfo":
                raw_gps = exif_data.get_ifd(tag_id)
                
                for key in raw_gps:
                    decoded_name = GPSTAGS.get(key, key)
                    gps_info[decoded_name] = raw_gps[key]
        if 'GPSLatitude' not in gps_info or 'GPSLatitudeRef' not in gps_info:
            return {"timestamp": timestamp, "camera_model": camera_model, "latitude": '', "longitude": ''}

        lat = _get_decimal_from_dms(gps_info['GPSLatitude'], gps_info['GPSLatitudeRef'])
        lon = _get_decimal_from_dms(gps_info['GPSLongitude'], gps_info['GPSLongitudeRef'])
        
        return {"timestamp": timestamp, "camera_model": camera_model, "latitude": lat, "longitude": lon}

if __name__ == "__main__":
    # img_file = "E:\\Coding\\Image Tagging\\Test Data\\IMG_9742.png"
    img_file = "E:\\OneDrive\\Pictures\\Camera Roll\\2025\\02\\20250221_024724935_iOS.heic"
    prompt = "Return only a JSON list of 5 to 10 tags for this image."
    start_time = time.time()
    result = query(img_file, prompt)
    # result = get_metadata(img_file)
    print("Result:", result)
    print(f"Total time: {time.time() - start_time:.2f} seconds.")