import os
import io
from PIL import Image, ImageOps
from pillow_heif import register_heif_opener
from fastapi import FastAPI, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List, Any

from database.search import search, on_this_day, get_image_details

register_heif_opener()

app = FastAPI(title="Photos API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/on-this-day")
def api_on_this_day():
    return {"data": on_this_day()}

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
    details = get_image_details(path)
    return {"data": details}

@app.get("/api/image")
def get_image(path: str):
    if not os.path.exists(path):
        return {"error": "File not found"}

    try:
        with Image.open(path) as img:
            img = ImageOps.exif_transpose(img)
            img.thumbnail((400, 400))
            if img.mode != "RGB":
                img = img.convert("RGB")
            
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=70)
            return Response(content=buf.getvalue(), media_type="image/jpeg")
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)