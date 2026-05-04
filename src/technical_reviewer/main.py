from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import uuid
import os
from technical_reviewer.crew import TechnicalReviewerCrew
from technical_reviewer.database import init_db, create_job, update_job_status, get_job

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(lifespan=lifespan)

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg"}

def run_crew_job(job_id: str, file_path: str, output_name: str):
    update_job_status(job_id, "running")
    try:
        inputs = {
            "file_path": file_path,
            "output_name": output_name
        }
        TechnicalReviewerCrew().crew().kickoff(inputs=inputs)
        update_job_status(job_id, "completed")
    except Exception as e:
        update_job_status(job_id, f"failed: {str(e)}")

@app.post("/analyze-architecture")
async def analyze(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    extension = os.path.splitext(file.filename)[1].lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF, PNG, JPG, and JPEG are supported.")
        
    job_id = str(uuid.uuid4())
    safe_filename = f"{job_id}{extension}"
    file_path = os.path.join(UPLOAD_DIR, safe_filename)
    output_name = os.path.join(OUTPUT_DIR, f"report_{job_id}")

    content = await file.read()
    with open(file_path, "wb") as buffer:
        buffer.write(content)

    create_job(job_id, "pending", file_path, output_name)
    background_tasks.add_task(run_crew_job, job_id, file_path, output_name)

    return {
        "message": "Analysis started",
        "job_id": job_id
    }

@app.get("/status/{job_id}")
async def get_status(job_id: str):
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"job_id": job_id, "status": job["status"]}

@app.get("/download/{job_id}/{format}")
async def download_report(job_id: str, format: str):
    if format not in ["pdf", "docx"]:
        raise HTTPException(status_code=400, detail="Format must be pdf or docx")
    
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Job is not completed yet")
        
    file_path = f"{job['output_name']}.{format}"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Report file not found")
        
    return FileResponse(path=file_path, filename=f"architecture_report_{job_id}.{format}")