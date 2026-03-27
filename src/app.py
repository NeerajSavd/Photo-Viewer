import os
import io
from PIL import Image, ImageOps
from pillow_heif import register_heif_opener
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import uvicorn
from database.search import search, on_this_day, image_details, image_map, recent_images, library_stats
from image_tagging import run_analysis

register_heif_opener()

app = FastAPI(title="Photos API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/sync")
def api_sync():
    try:
        run_analysis()
    except:
        return {"error": "Sync failed"}
    return {"message": "Sync successful"}

@app.get("/api/recent")
def api_recent():
    return {"data": recent_images()}

@app.get("/api/on-this-day")
def api_on_this_day(date: Optional[str] = None):
    return {"data": on_this_day(date)}

@app.get("/api/map")
def get_map():
    return {"data": image_map()}

@app.get("/api/stats")
def api_stats():
    return {"data": library_stats()}

@app.get("/api/search")
def api_search(
    query: Optional[str] = "", 
    city: Optional[str] = "", 
    dateStart: Optional[str] = None, 
    dateEnd: Optional[str] = None
):
    results = search(query.lower(), city, dateStart, dateEnd)
    return {"data": results}

@app.get("/api/details")
def api_details(path: str):
    details = image_details(path)
    return {"data": details}

@app.get("/api/image")
def get_image(path: str, size: Optional[str] = "thumb"):
    if not os.path.exists(path):
        return {"error": "File not found"}

    try:
        with Image.open(path) as img:
            img = ImageOps.exif_transpose(img)
            if size == "full":
                img.thumbnail((1920, 1920))
            else:
                img.thumbnail((500, 500))
            
            if img.mode != "RGB":
                img = img.convert("RGB")
            
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=70)
            return Response(content=buf.getvalue(), media_type="image/jpeg")
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)