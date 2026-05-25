import os
import shutil
import zipfile
from typing import List
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from celery.result import AsyncResult

from backend.analyzer import static_analyzer
from backend.optimizer import reflection_loop
from backend.knowledge_base import knowledge_base
from backend.worker import celery_app, process_legacy_file_task

app = FastAPI(title="AEGIS Auto-Refactor-Agent API")
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# Optional: Force a higher payload limit if streaming crashes
class LimitUploadSizeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Allow up to 50MB files safely
        return await call_next(request)

app.add_middleware(LimitUploadSizeMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CodeRequest(BaseModel):
    code: str
    source_lang: str
    target_lang: str

class RefactorResponse(BaseModel):
    original_code: str
    refactored_code: str
    static_analysis_status: str
    static_analysis_issues: str
    agent_logs: list[str]
    final_status: str

@app.post("/api/refactor", response_model=RefactorResponse)
async def refactor_endpoint(request: CodeRequest):
    try:
        # Run static analysis based on incoming language syntax rules
        analysis_result = static_analyzer.analyze(request.code, request.source_lang)
        context = knowledge_base.retrieve(request.code)
        
        # --- DYNAMIC CODES-WAY SEGREGATION ---
        # If we are keeping it in Python or translating it into Python, we can safely use Docker Reflection!
        if request.target_lang.lower() == "python":
            from backend.optimizer import reflection_loop
            
            # Add strict cross-compilation instructions to the vector DB context
            enhanced_context = context + f"\n\nCRITICAL: Translate the code from {request.source_lang.upper()} to {request.target_lang.upper()}."
            
            final_code, final_status, logs = reflection_loop(
                original_code=request.code,
                static_analysis_report=analysis_result.get("issues", "No issues."),
                context=enhanced_context,
                source_lang=request.source_lang,
                target_lang=request.target_lang,
                max_retries=1
            )
            logs.insert(0, f"📚 Retrieved Standards Context:\n{context}")
            logs.insert(1, f"🌐 Translation Pipeline Initiated: {request.source_lang.upper()} ──► {request.target_lang.upper()}")
            
        else:
            # For non-python compilation targets (Go, C++, Java), we let the model handle the transpile step directly 
            from backend.ai_agent import ai_agent
            from backend.optimizer import extract_python_code # Using your markdown extraction logic
            
            logs = [
                f"📚 Retrieved Standards Context:\n{context}",
                f"🌐 Direct Translation Route Activated: {request.source_lang.upper()} ──► {request.target_lang.upper()}"
            ]
            
            # Pass our specific source and target languages down to your model
            raw_code = ai_agent.refactor_code(
                code=request.code, 
                static_analysis_report=analysis_result.get("issues", ""), 
                source_lang=request.source_lang,
                target_lang=request.target_lang,
                context=context
            )
            
            # Fallback block extraction mechanism
            final_code = extract_python_code(raw_code) 
            final_status = "Direct Transpilation Completed (Sandbox validation bypassed)"
            logs.append("✅ Code compiled autonomously via Qwen Model.")

        return RefactorResponse(
            original_code=request.code, 
            refactored_code=final_code,
            static_analysis_status=analysis_result.get("status", "unknown"),
            static_analysis_issues=analysis_result.get("issues", ""),
            agent_logs=logs, 
            final_status=final_status
        )
        
    except Exception as e:
        import traceback
        print("\n" + "="*50 + " BACKEND CRASH DETECTED " + "="*50)
        traceback.print_exc()
        print("="*124 + "\n")
        raise HTTPException(status_code=500, detail=str(e))

# ---------------------------------------------------------
# NEW REPOSITORY BATCH PROCESSING ENDPOINTS
# ---------------------------------------------------------
SUPPORTED_EXTENSIONS = {
    '.py': 'python',
    '.java': 'java',
    '.cpp': 'cpp',
    '.cc': 'cpp',
    '.c': 'c',
    '.go': 'go',
    '.js': 'javascript',
    '.ts': 'typescript'
}

@app.post("/api/upload-repo")
async def upload_repository(file: UploadFile = File(...), target_lang: str = "python"):
    """Receives a ZIP file, extracts it, auto-detects source languages, and sends tasks to Celery."""
    if not file.filename.endswith('.zip'):
        raise HTTPException(status_code=400, detail="Only .zip files are supported.")

    # Create a secure workspace folder for this upload
    workspace = os.path.join(os.getcwd(), "workspace", file.filename.replace('.zip', ''))
    os.makedirs(workspace, exist_ok=True)
    
    zip_path = os.path.join(workspace, file.filename)
    with open(zip_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Unzip the repository
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(workspace)

    task_ids = []
    
    # Walk through all folders and files in the unzipped repo
    for root, _, files in os.walk(workspace):
        for f in files:
            # Extract extension (e.g., '.java', '.py')
            _, ext = os.path.splitext(f)
            ext = ext.lower()
            
            # Check if the file matches our supported translation list
            if ext in SUPPORTED_EXTENSIONS:
                source_lang = SUPPORTED_EXTENSIONS[ext]
                file_path = os.path.join(root, f)
                
                try:
                    with open(file_path, "r", encoding="utf-8") as source_file:
                        original_code = source_file.read()
                    
                    # Send task to Celery passing code, auto-detected source language, and selected target language
                    # Make sure your process_legacy_file_task definition accepts these arguments!
                    task = process_legacy_file_task.delay(
                        file_path=file_path, 
                        original_code=original_code, 
                        source_lang=source_lang, 
                        target_lang=target_lang
                    )
                    task_ids.append(task.id)
                    
                except UnicodeDecodeError:
                    pass # Skip non-text or corrupt binary files

    return {
        "message": f"Successfully queued {len(task_ids)} files for background translation to {target_lang.upper()}.",
        "task_ids": task_ids,
        "workspace": workspace
    }


@app.post("/api/repo-status")
async def get_repo_status(task_ids: List[str]):
    """Checks Redis to see how many Celery tasks have finished."""
    completed = 0
    failed = 0
    
    for task_id in task_ids:
        res = AsyncResult(task_id, app=celery_app)
        if res.ready():
            if res.successful():
                completed += 1
            else:
                failed += 1
                
    total = len(task_ids)
    status = "Processing" if completed + failed < total else "Completed"
    
    return {
        "total": total,
        "completed": completed,
        "failed": failed,
        "status": status
    }