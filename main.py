from fastapi import FastAPI, HTTPException
import gdown
import os
import boto3
from botocore.client import Config
from uuid import uuid4

# --- Config ---
BUCKET_NAME = "gdrive-files"
R2_ENDPOINT = "https://a94afe102362fdcb030e48f2b338c379.r2.cloudflarestorage.com"
R2_ACCESS_KEY_ID = "f892ae332b5659fabf27065778ef29b6"
R2_SECRET_ACCESS_KEY = "4037ef6b43774f7cd6396d7ec17bce9ba36f5123c7e07e0ca9934b65a9bba59b"

# --- FastAPI setup ---
app = FastAPI()

@app.get("/download")
def download(file_id: str):
    try:
        # Generate temporary file path
        filename = f"{uuid4().hex}.mp4"
        output_path = f"/tmp/{filename}"

        # Download from Google Drive
        url = f"https://drive.google.com/uc?id={file_id}"
        gdown.download(url, output_path, quiet=False)

        # Check if downloaded
        if not os.path.exists(output_path):
            raise HTTPException(status_code=404, detail="Download failed")

        # Upload to R2
        session = boto3.session.Session()
        s3 = session.client(
            service_name="s3",
            aws_access_key_id=R2_ACCESS_KEY_ID,
            aws_secret_access_key=R2_SECRET_ACCESS_KEY,
            endpoint_url=R2_ENDPOINT,
            config=Config(signature_version="s3v4"),
        )

        r2_key = f"{file_id}.mp4"

        with open(output_path, "rb") as f:
            s3.upload_fileobj(f, BUCKET_NAME, r2_key)

        # Delete temp file
        os.remove(output_path)

        # Construct public URL
        public_url = f"{R2_ENDPOINT}/{r2_key}"

        return { "download_url": public_url }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
