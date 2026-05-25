import ollama

class AIAgent:
    def __init__(self, model_name="qwen2.5-coder:7b"):
        self.model_name = model_name

    def refactor_code(self, code: str, static_analysis_report: str, source_lang: str, target_lang: str, context: str = "") -> str:
        prompt = f"""You are an elite multi-language systems architect. Your strict directive is to translate and optimize legacy code.

### TRANSLATION TASK:
Convert this code from {source_lang.upper()} into highly optimized, idiomatic {target_lang.upper()}.

### STRICT INSTRUCTIONS:
1. You MUST translate the logic fully. Do not leave placeholder comments.
2. Adapt the code to use the modern paradigms of the target language (e.g., if target is Python, use list comprehensions; if Go, handle errors idiomatically).
3. Optimize the algorithmic time and space complexity.
4. Output ONLY valid {target_lang.upper()} code inside ```{target_lang} ``` blocks. No explanations.
5. Add strict type hints to ALL function signatures AND variable assignments (e.g., def func(a: list[int]) -> list: and my_list: list[str] = [...]).
6. Any global execution tests, print statements, or dummy verification data MUST be strictly wrapped inside a proper `if __name__ == "__main__":` block guard.

### ORIGINAL {source_lang.upper()} CODE:
{code}
"""
        try:
            # Added temperature 0.1 to force precise, deterministic code generation
            response = ollama.chat(model=self.model_name, messages=[
                {
                    'role': 'system',
                    'content': 'You are a code refactoring tool. Output only the modified code in the target language.'
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ], options={"temperature": 0.1})

            return response['message']['content']

        except Exception as e:
            # Safe fallback if Ollama crashes
            return f"Error generating refactor: {e}"

    def generate_unit_tests(self, original_code: str, target_lang: str = "python") -> str:
        """
        Generates a strict suite of assertion tests based on the original legacy logic.
        """
        prompt = f"""You are an elite QA Automation Engineer.
Your job is to read legacy code and write a comprehensive test suite to verify its mathematical outputs.

### LEGACY CODE:
{original_code}

### STRICT INSTRUCTIONS:
1. Write a series of strict {target_lang.upper()} `assert` statements.
2. CRITICAL NAMING RULE: Translate legacy function names into the idiomatic case of the target language.
3. NO HARDCODED MATH: You are an AI, which means you hallucinate arithmetic. DO NOT hardcode the expected output arrays (e.g., NEVER write `== [80.0, 40.0]`). 
4. DYNAMIC CALCULATION: Instead of hardcoding, calculate the expected result PROGRAMMATICALLY inside the test script using basic Python logic, then assert it equals the refactored function's output.
5. Output ONLY valid {target_lang.upper()} code inside ```{target_lang} ``` blocks. No explanations.

### EXAMPLE OF DYNAMIC TESTING:
```python
# Setup inputs
inputs = [100.0, 50.0, 10.0]
rate = 0.2
# Calculate expected dynamically using Python
expected = [p - (p * rate) for p in inputs if p - (p * rate) > 0]
# Assert
assert calculate_discount(inputs, rate) == expected
"""
        try:
            response = ollama.chat(model=self.model_name, messages=[
                {
                    'role': 'system',
                    'content': 'You are a strict QA Automation Engineer. Output only the requested test code.'
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ], options={"temperature": 0.1})

            raw_response = response['message']['content']
            from backend.optimizer import extract_python_code
            return extract_python_code(raw_response)

        except Exception as e:
            return f"Error generating tests: {e}"

ai_agent = AIAgent()