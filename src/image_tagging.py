import os
import json
import tqdm
from concurrent.futures import ThreadPoolExecutor
from analysis import query, get_metadata
from database import init_db, check_image_exists, insert_image, insert_tags
from dotenv import load_dotenv
import time

load_dotenv()
db_path = os.getenv("DB_PATH")

CONCURRENT_THREADS = 12
prompt = "Return only a JSON list of 5 to 10 single-word tags for this image."

def get_image_files(folder_path):
    images = [os.path.join(folder_path, f) for f in os.listdir(folder_path)
              if f.lower().endswith(('.png', '.jpg', '.jpeg', '.heic', '.webp'))]
    
    new_images = []
    conn = init_db()
    for img in images:
        if not check_image_exists(conn, img):
            new_images.append(img)
    conn.close()

    return new_images

def analyze_folder(images):
    conn = init_db()
    for img_path in tqdm.tqdm(images, desc="Extracting metadata"):
        metadata = get_metadata(img_path)
        insert_image(conn, img_path, metadata)
    
    results = []
    with ThreadPoolExecutor(max_workers=CONCURRENT_THREADS) as executor:
        results = list(tqdm.tqdm(executor.map(lambda img_path: (img_path, query(img_path, prompt)), images), total=len(images), desc="Analyzing images"))

    for _, (img_path, tags_json) in tqdm.tqdm(enumerate(results), total=len(results), desc="Saving results"):
        try:
            tags_json = tags_json.replace("```json", '').replace("```", '').replace("\n", '').strip()
            tags = json.loads(tags_json)
        except (json.JSONDecodeError, AttributeError):
            tags = [] 
        insert_tags(conn, img_path, tags)
    
    conn.close()

def run_analysis():
    total = 0
    with open("folders.txt", "r") as file:
        for line in file:
            parent_folder = line.strip()

            for root, _, _ in os.walk(parent_folder):
                print(f"Processing folder: {root}")
                images = get_image_files(root)
                if len(images) != 0:
                    analyze_folder(images)
                    total += len(images)
                    print(f"Processed {len(images)} images in folder: {root}")
    print(f"Total images processed: {total}")

if __name__ == "__main__":
    start_time = time.time()
    run_analysis()
    print(f"Total time: {time.time() - start_time:.2f} seconds.")