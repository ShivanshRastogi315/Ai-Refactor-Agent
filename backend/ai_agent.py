import ollama

class AIAgent:
    def __init__(self, model_name="qwen2.5-coder:7b"):
        self.model_name = model_name

    def refactor_code(self, code: str, static_analysis_report: str, context: str = "") -> str:
        prompt = f"""You are an expert autonomous code refactoring agent.
        
        Context/Standards:
        {context}
        
        Static Analysis Report:
        {static_analysis_report}
        
        Original Code:
        {code}
        
        Please provide the fully refactored and optimized code. Fix any issues mentioned in the Static Analysis Report.
        Only output the code, no explanations.
        """
        
        response = ollama.chat(model=self.model_name, messages=[
            {
                'role': 'user',
                'content': prompt
            }
        ])
        
        return response['message']['content']

ai_agent = AIAgent()