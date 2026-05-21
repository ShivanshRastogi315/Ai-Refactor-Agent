import re
from backend.ai_agent import ai_agent
from backend.sandbox import sandbox

def extract_python_code(llm_output: str) -> str:
    """Extracts raw code from markdown blocks if the LLM adds them."""
    match = re.search(r'```python\n(.*?)\n```', llm_output, re.DOTALL)
    if match:
        return match.group(1)
    return llm_output.strip()

def reflection_loop(original_code: str, static_analysis_report: str, context: str = "", max_retries: int = 1) -> tuple:
    """
    Orchestrates the refactoring and verifies it via sandboxed execution.
    Returns: (final_code, status, execution_logs)
    """
    logs = ["🔄 Starting Reflection Loop..."]
    
    # Attempt 1: Initial Generation
    logs.append("🧠 Agent generating initial refactored code...")
    current_code = ai_agent.refactor_code(original_code, static_analysis_report, context)
    clean_code = extract_python_code(current_code)
    
    for attempt in range(max_retries + 1):
        logs.append(f"▶️ Executing Attempt {attempt + 1} in Docker Sandbox...")
        
        # Execute the code in the isolated Docker container
        execution_result = sandbox.execute_python(clean_code)
        
        if execution_result["success"]:
            logs.append("✅ Execution Successful! Code is structurally sound.")
            return clean_code, "Success", logs
        else:
            error_traceback = execution_result["output"]
            logs.append(f"❌ Execution Failed. Error:\n{error_traceback}")
            
            if attempt < max_retries:
                logs.append("🛠️ Agent is reflecting on the error and generating a fix...")
                # Modify the prompt to include the error traceback for self-correction
                correction_prompt = f"""
                Your previously refactored code threw a runtime error during sandboxed execution.
                
                Previous Code:
                {clean_code}
                
                Runtime Error / Traceback:
                {error_traceback}
                
                Please fix the error and provide the corrected, fully refactored Python code.
                Only output the code, no explanations.
                """
                current_code = ai_agent.refactor_code(original_code, static_analysis_report, context + "\n\n" + correction_prompt)
                clean_code = extract_python_code(current_code)
            else:
                logs.append("⚠️ Max retries reached. Returning the last generated code with errors.")
                return clean_code, "Failed (Runtime Errors)", logs

    return clean_code, "Failed", logs