from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
import gdown
import os

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/download")
def download(file_id: str):
    try:
        output_path = f"static/{file_id}.mp4"

        # If file already exists, return its path
        if os.path.exists(output_path):
            return { "download_url": f"/static/{file_id}.mp4" }

        # Build the gdown URL
        url = f"https://drive.google.com/uc?id={file_id}"
        gdown.download(url, output_path, quiet=False)

        # Check again
        if not os.path.exists(output_path):
            raise HTTPException(status_code=404, detail="Download failed")

        return { "download_url": f"/static/{file_id}.mp4" }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
