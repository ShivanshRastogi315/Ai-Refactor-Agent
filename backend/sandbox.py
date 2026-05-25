import docker
import tempfile
import os

class DockerSandbox:
    def __init__(self):
        try:
            self.client = docker.from_env()
            # Pre-pull the lightweight python image to avoid delays during execution
            self.client.images.pull("python:3.10-slim")
        except docker.errors.DockerException as e:
            print(f"Warning: Docker is not running or accessible. {e}")
            self.client = None

    def execute_python(self, code: str, timeout_seconds: int = 5) -> dict:
        if not self.client:
            return {"success": False, "output": "Docker is not running on the host machine."}

        # Create a temporary directory to mount into the container
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, "script.py")
            with open(file_path, "w") as f:
                f.write(code)

            try:
                # Run the container with heavy restrictions
                container = self.client.containers.run(
                    image="python:3.10-slim",
                    # Use 'timeout' utility to prevent infinite loops (e.g., while True:)
                    command=["sh", "-c", f"timeout {timeout_seconds} python /app/script.py"],
                    volumes={temp_dir: {'bind': '/app', 'mode': 'ro'}},
                    working_dir="/app",
                    mem_limit="128m",          # Restrict memory to 128MB
                    network_disabled=True,     # SECURITY: No internet access for the code
                    remove=True,               # Auto-delete container after run
                    stdout=True,
                    stderr=True,
                    environment={"PYTHONUNBUFFERED": "1"} 
                )
                return {"success": True, "output": container.decode('utf-8').strip()}
                
            except docker.errors.ContainerError as e:
                # This catches non-zero exit codes (syntax errors, runtime crashes)
                error_msg = e.stderr.decode('utf-8').strip() if e.stderr else "Unknown Runtime Error/Timeout"
                return {"success": False, "output": error_msg}
            except Exception as e:
                return {"success": False, "output": f"System Error: {str(e)}"}

sandbox = DockerSandbox()