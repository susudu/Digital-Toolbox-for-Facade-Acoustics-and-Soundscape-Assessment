from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import subprocess, os, uuid

app = FastAPI(title="Digital Toolbox API")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs("results", exist_ok=True)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Digital Toolbox API!"}

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")
    
    # Save uploaded file
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Run the processing script (asynchronously)
    subprocess.Popen(["python", "app/process_script.py", file_path])

    return JSONResponse({
        "message": "File uploaded successfully and processing started.",
        "file_id": file_id,
        "filename": file.filename
    })
