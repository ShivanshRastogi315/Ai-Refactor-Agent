import subprocess
import tempfile
import os

class StaticAnalyzer:
    def __init__(self):
        self.supported_languages = {
            'python': self._analyze_python,
            # Placeholders for future C and Java integration
            'c': self._analyze_c, 
            'java': self._analyze_java 
        }

    def analyze(self, code: str, language: str = 'python') -> dict:
        if language not in self.supported_languages:
            return {"status": "skipped", "issues": f"Static analysis not supported for {language}."}
        
        return self.supported_languages[language](code)

    def _analyze_python(self, code: str) -> dict:
        # Write code to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".py", mode='w') as temp_file:
            temp_file.write(code)
            temp_file_path = temp_file.name

        try:
            # Run pylint on the temporary file
            result = subprocess.run(
                ['pylint', temp_file_path, '--output-format=text', '--disable=C,R'], 
                capture_output=True, text=True
            )
            
            issues = result.stdout.strip()
            status = "passed" if result.returncode == 0 else "failed"
            
            return {"status": status, "issues": issues}
        finally:
            os.remove(temp_file_path)

    def _analyze_c(self, code: str) -> dict:
        # To be implemented with cppcheck
        return {"status": "pending", "issues": "C analysis coming soon"}

    def _analyze_java(self, code: str) -> dict:
        # To be implemented with checkstyle
        return {"status": "pending", "issues": "Java analysis coming soon"}

# Initialize singleton
static_analyzer = StaticAnalyzer()