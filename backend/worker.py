import os
from celery import Celery
from backend.optimizer import reflection_loop
from backend.knowledge_base import knowledge_base
from backend.analyzer import static_analyzer

celery_app = Celery(
    "aegis_worker",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

@celery_app.task(name="process_legacy_file")
def process_legacy_file_task(file_path: str, original_code: str, source_lang: str = "python", target_lang: str = "python"):
    filename = os.path.basename(file_path)
    print(f"\n{'='*40}")
    print(f"🚀 [STARTING] {filename} ({source_lang.upper()} ──► {target_lang.upper()})")
    
    try:
        # 1. Run actual static analysis on the file
        analysis_result = static_analyzer.analyze(original_code, source_lang)
        context = knowledge_base.retrieve(original_code)
        
        # 2. Setup structural optimization prompts
        strict_context = context + f"\n\nCRITICAL INSTRUCTION: You MUST translate this code from {source_lang.upper()} to {target_lang.upper()} and optimize its time and space complexity. Replace O(n^2) loops with O(n) implementations. Do not return the original code unchanged."
        
        # --- 3. DYNAMIC TARGET CHECKING BLOCK ---
        if target_lang.lower() == "python":
            # Use full Docker reflection safety checks for Python compilations
            final_code, final_status, logs = reflection_loop(
                original_code=original_code,
                static_analysis_report=analysis_result.get("issues", "No issues."),
                context=strict_context,
                source_lang=source_lang,
                target_lang=target_lang,
                max_retries=3
            )
        else:
            # For non-Python targets (Java, Go, C++), use direct transpilation path 
            # to prevent Python sandbox interpreter collisions!
            from backend.ai_agent import ai_agent
            from backend.optimizer import extract_python_code # Extracts markdown block
            
            print(f"🌐 Direct Code Generation Activated (Bypassing Python Sandbox for {target_lang.upper()})")
            
            raw_code = ai_agent.refactor_code(
                code=original_code,
                static_analysis_report=analysis_result.get("issues", ""),
                context=strict_context,
                source_lang=source_lang,
                target_lang=target_lang
            )
            final_code = extract_python_code(raw_code)
            final_status = "Success"
            
        print(f"🧠 [STATUS] {final_status}")
        
        if final_status == "Success":
            # 4. Handle dynamic extension conversion
            base_path, _ = os.path.splitext(file_path)
            ext_mapping = {
                "python": ".py", "go": ".go", "java": ".java", 
                "cpp": ".cpp", "c": ".c", "javascript": ".js", "typescript": ".ts"
            }
            new_ext = ext_mapping.get(target_lang.lower(), ".txt")
            output_file_path = base_path + new_ext
            
            # If the language target changed the extension, clean up the original old file
            if file_path != output_file_path and os.path.exists(file_path):
                os.remove(file_path)
                print(f"🗑️ [CLEANUP] Removed old legacy file: {filename}")

            with open(output_file_path, "w", encoding="utf-8") as f:
                f.write(final_code)
            print(f"✅ [SAVED] Wrote optimized code to {os.path.basename(output_file_path)}.")
            return {"file": output_file_path, "status": final_status}
            
        else:
            print(f"⚠️ [ABORTED] {filename} failed logic generation path.")
            print(f"🔍 [TRACEBACK]:\n{logs[-2]}")
            return {"file": file_path, "status": final_status}
                
    except Exception as e:
        print(f"❌ [CRASH] Fatal error on {filename}: {str(e)}")
        return {"file": file_path, "status": f"Failed: {str(e)}"}