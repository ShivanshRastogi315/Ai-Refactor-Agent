import re
from backend.ai_agent import ai_agent
from backend.sandbox import sandbox
from backend.chunker import semantic_chunking

def extract_python_code(llm_output: str) -> str:
    """Extracts raw code from markdown blocks if the LLM adds them."""
    match = re.search(r'```python\n(.*?)\n```', llm_output, re.DOTALL)
    if match:
        return match.group(1)
    return llm_output.strip()

def reflection_loop(
    original_code: str, 
    static_analysis_report: str, 
    context: str = "", 
    source_lang: str = "python", 
    target_lang: str = "python", 
    max_retries: int = 1
) -> tuple:
    """
    Orchestrates AST-chunked refactoring, automated QA generation, and verifies via sandboxed execution.
    Supports multi-language translation and optimization paths.
    Returns: (final_code, status, execution_logs)
    """
    logs = ["🔄 Starting Reflection Loop..."]
    
    # --- PHASE 1: AUTOMATED QA TEST GENERATION ---
    logs.append("🧪 QA Agent analyzing legacy logic and writing automated test suite...")
    test_suite = ai_agent.generate_unit_tests(original_code, target_lang)
    logs.append("✅ Automated Test Suite generated successfully.")

    # --- PHASE 2: DYNAMIC CHUNKING & REFACTORING ---
    logs.append("✂️ Analyzing file size for chunking...")
    
    # DYNAMIC THRESHOLD: If the file is under 2000 characters (~50 lines), process it whole!
    if len(original_code) < 2000:
        logs.append("⚡ File is small enough for direct full-context processing (Bypassing Chunker).")
        chunks = [original_code]
    else:
        logs.append("✂️ Semantically chunking code to prevent GPU memory overflow...")
        chunks = semantic_chunking(original_code)
        logs.append(f"📦 AST parsed codebase into {len(chunks)} isolated logic chunk(s).")
    
    assembled_clean_code = []
    
    # Attempt 1: Chunk-by-Chunk Generation
    logs.append("🧠 Agent generating refactored code (processing chunks)...")
    for i, chunk in enumerate(chunks):
        chunk_refactored = ai_agent.refactor_code(
            code=chunk, 
            static_analysis_report=static_analysis_report, 
            context=context,
            source_lang=source_lang,
            target_lang=target_lang
        )
        assembled_clean_code.append(extract_python_code(chunk_refactored))
        
    # Stitch the optimized base code back together
    base_optimized_code = "\n\n".join(assembled_clean_code)
    
    # --- PHASE 3: EXECUTION & REFLECTION LOOP ---
    for attempt in range(max_retries + 1):
        logs.append(f"▶️ Executing Attempt {attempt + 1} with QA Suite in Docker Sandbox...")
        
        # Inject the generated tests at the bottom of the script for the Docker container
        current_code_with_tests = f"{base_optimized_code}\n\n# --- AUTOMATED TESTS ---\n{test_suite}\nprint('All tests passed!')"
        
        # Execute the FULL unified code in the isolated Docker container
        execution_result = sandbox.execute_python(current_code_with_tests)
        
        # Verify the script didn't crash AND the assertions passed
        if execution_result["success"] and "All tests passed!" in execution_result.get("output", ""):
            logs.append("✅ QA Execution Successful! Code logic is mathematically verified.")
            
            # ──► CRITICAL: We return the base code, dropping the temporary test suite!
            return base_optimized_code, "Success", logs
            
        else:
            error_traceback = execution_result["output"]
            logs.append(f"❌ Execution Failed. Error:\n{error_traceback}")
            
            if attempt < max_retries:
                logs.append("🛠️ Agent is reflecting on the global error and generating a fix...")
                
                # Self-Correction happens on the clean base script
                correction_prompt = f"""
                Your previously assembled refactored code threw a runtime error or failed QA assertions during sandboxed execution.
                
                Previous Code:
                {base_optimized_code}
                
                QA Assertion Failure / Traceback:
                {error_traceback}
                
                Please fix the logical error so it passes the assertions and provide the corrected, fully refactored {target_lang.upper()} code.
                Only output the code, no explanations.
                """
                
                fixed_code = ai_agent.refactor_code(
                    code=base_optimized_code, 
                    static_analysis_report=static_analysis_report, 
                    context=context + "\n\n" + correction_prompt,
                    source_lang=target_lang,  
                    target_lang=target_lang
                )
                base_optimized_code = extract_python_code(fixed_code)
                
                # REBUILD THE EXECUTION STRING FOR THE NEXT LOOP ATTEMPT
                current_code_with_tests = f"{base_optimized_code}\n\n# --- AUTOMATED TESTS ---\n{test_suite}\nprint('All tests passed!')"
                
            else:
                logs.append("⚠️ Max retries reached. Returning the last generated code with errors.")
                return base_optimized_code, "Failed (QA Test Failures)", logs

    return base_optimized_code, "Failed", logs