import os
import json
import tqdm
from concurrent.futures import ThreadPoolExecutor
from analysis import query, get_metadata
from database.database import init_db
from database.operations import check_image_exists, insert_image, insert_tags, delete_image
from dotenv import load_dotenv
import time

load_dotenv()
db_path = os.getenv("DB_PATH")

CONCURRENT_THREADS = 12
prompt = "Return only a JSON list of 5 to 10 single-word tags for this image."

def handle_query(img_path, prompt):
    """Handle query with error handling, returning (img_path, None) on failure."""
    try:
        tags_json = query(img_path, prompt)
        return (img_path, tags_json)
    except Exception as e:
        print(e)
        return (img_path, None)

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
    failed_images = []
    
    for img_path in tqdm.tqdm(images, desc="Extracting metadata"):
        try:
            metadata = get_metadata(img_path)
            insert_image(conn, img_path, metadata)
        except Exception as e:
            print(f"Failed to extract metadata for {img_path}: {e}")
            failed_images.append(img_path)
    
    images = [img for img in images if img not in failed_images]
    for img_path in failed_images:
        delete_image(conn, img_path)

    failed_tagging = []
    results = []
    with ThreadPoolExecutor(max_workers=CONCURRENT_THREADS) as executor:
        results = list(tqdm.tqdm(executor.map(lambda img_path: handle_query(img_path, prompt), images), total=len(images), desc="Analyzing images"))

    for img_path, tags_json in tqdm.tqdm(results, total=len(results), desc="Saving results"):
        if tags_json is None:
            failed_tagging.append(img_path)
            continue
        try:
            tags_json = tags_json.replace("```json", '').replace("```", '').replace("\n", '').strip()
            tags = json.loads(tags_json)
        except (json.JSONDecodeError, AttributeError):
            tags = []
            failed_tagging.append(img_path)
        
        insert_tags(conn, img_path, tags)
    
    for img_path in failed_tagging:
        print(f"Failed to tag {img_path}, removing from database")
        delete_image(conn, img_path)
    
    conn.close()

def test_image_tagging(folder_path):
    images = [os.path.join(folder_path, f) for f in os.listdir(folder_path)
              if f.lower().endswith(('.png', '.jpg', '.jpeg', '.heic', '.webp'))]
    print(f"Found {len(images)} images to process")
    
    results = []
    with ThreadPoolExecutor(max_workers=CONCURRENT_THREADS) as executor:
        results = list(tqdm.tqdm(executor.map(lambda img_path: handle_query(img_path, prompt), images), total=len(images), desc="Analyzing images"))
    
    successful_images = []
    failed_images = []
    
    for img_path, tags_json in results:
        if tags_json is None:
            failed_images.append((img_path, "Query failed"))
            continue
        try:
            tags_json = tags_json.replace("```json", '').replace("```", '').replace("\n", '').strip()
            tags = json.loads(tags_json)
            successful_images.append((img_path, tags))
        except (json.JSONDecodeError, AttributeError) as e:
            failed_images.append((img_path, f"JSON parse error: {e}"))
    
    print("\n" + "="*50)
    if failed_images:
        print("\nFailed images:")
        for img_path, error in failed_images:
            print(f"  {os.path.basename(img_path)}: {error}")


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
    test_folder = "E:\\OneDrive\\Pictures\\Camera Roll\\2025\\02"
    start_time = time.time()
    test_image_tagging(test_folder)
    print(f"Total time: {time.time() - start_time:.2f} seconds.")
    
    # run_analysis()