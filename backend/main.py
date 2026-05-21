from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from backend.analyzer import static_analyzer
from backend.optimizer import reflection_loop
from backend.knowledge_base import knowledge_base # ADD THIS IMPORT

app = FastAPI(title="Auto-Refactor-Agent API")

class CodeRequest(BaseModel):
    code: str
    language: str = "python"

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
        # 1. Run Static Analysis
        analysis_result = static_analyzer.analyze(request.code, request.language)
        
        # 2. Retrieve Dynamic Context via AST & RAG
        # This will now pull specific rules based on the code structure!
        context = knowledge_base.retrieve(request.code)
        
        # 3. Trigger the Docker Reflection Loop
        if request.language.lower() == "python":
            final_code, final_status, logs = reflection_loop(
                original_code=request.code,
                static_analysis_report=analysis_result.get("issues", "No issues."),
                context=context,
                max_retries=1
            )
            # Add context to logs so you can verify what rules were injected
            logs.insert(1, f"📚 Retrieved Standards Context:\n{context}")
        else:
            from backend.ai_agent import ai_agent
            from backend.optimizer import extract_python_code
            raw_code = ai_agent.refactor_code(request.code, analysis_result.get("issues", ""), context)
            final_code = extract_python_code(raw_code)
            final_status = "Skipped Execution (Language not supported)"
            logs = [f"📚 Retrieved Standards Context:\n{context}", "Execution skipped for non-Python language."]

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
        traceback.print_exc() # This will print the exact file name and line number that crashed
        print("="*124 + "\n")
        raise HTTPException(status_code=500, detail=str(e))