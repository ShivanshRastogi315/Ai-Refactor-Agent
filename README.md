# PRISM: Autonomous Code Refactoring Agent

An enterprise-grade, fully local AI-powered refactoring system designed to transform inefficient, syntactically broken, or poorly structured code into optimized, production-ready implementations. Moving beyond standard text generation, this agent employs a Reflection Architecture, utilizing Docker-based sandboxed execution to verify its own code, AST-driven chunking, automated Test-Driven Development (TDD), and a decoupled FastAPI/Celery backend for seamless batch repository processing.

## Abstract

Writing code is easy; maintaining clean, optimized, and scalable code is hard. Traditional static analyzers catch syntax errors but cannot refactor logic. Cloud-based LLMs can refactor logic but pose severe data privacy risks and frequently hallucinate variables or fail basic arithmetic during translation.

This project bridges that gap. By combining the local reasoning power of Qwen2.5-Coder with an isolated Docker execution sandbox, the agent acts as a senior developer. It reads the code, maps its Abstract Syntax Tree (AST) to prevent context window overflow, generates strict dynamic unit tests, refactors the solution, and most importantly—tests its own code. If the code crashes or fails the math assertions, the agent reads the runtime error traceback and self-corrects before presenting the final output.

All of this happens entirely locally, ensuring zero data leakage.

## Key Features & Use Cases

- **Algorithmic Optimization**: Automatically identifies $O(n^2)$ bottlenecks (like nested loops) and refactors them into $O(n)$ or $O(n \log n)$ solutions using optimized data structures and list comprehensions.
- **The Reflection Loop (Self-Healing)**: Executes generated code in a secure, network-disabled Docker container. If a runtime error or assertion failure occurs, the agent reads the traceback and attempts to fix its own mistake.
- **Dynamic TDD Generation**: Bypasses LLM mathematical hallucinations by forcing the QA agent to write programmatic Python tests, letting the sandbox dynamically calculate expected outcomes.
- **Distributed Batch Processing**: Utilizes a Redis and Celery message queue to process massive `.zip` repositories asynchronously, preventing UI lockups and CPU bottlenecks.
- **Privacy-First**: Powered by Ollama, running 100% offline on consumer hardware.

## Architecture & Methodology

The system operates on a highly structured, 5-stage pipeline:

1. **Automated QA Generation**: Before refactoring, a dedicated QA Agent analyzes the legacy logic and writes a strict suite of assertion tests to mathematically verify the expected outputs.
2. **AST Feature Extraction & Chunking**: The system parses the original code to extract structural boundaries. Small files bypass chunking, while massive enterprise files are split semantically to prevent GPU memory overflow.
3. **LLM Generation (Qwen2.5-Coder)**: The local LLM translates and optimizes the codebase into the target language, applying modern paradigms and strict type hinting.
4. **Sandboxed Verification (Docker)**: The newly generated code and the QA test suite are stitched together and mounted into an ephemeral `python:3.10-slim` Docker container. It is executed with strict memory constraints to prevent infinite loops.
5. **The Reflection Retry**: If the Docker container exits with an error code, the agent is fed the `stderr` traceback and given up to three retries to reflect on its logical failure and output a corrected script.

## Technologies Used

### Backend & Core Logic
- **FastAPI & Uvicorn**: High-performance async API routing.
- **Ollama (Qwen2.5 / DeepSeek)**: The core open-weight reasoning engine.
- **Redis & Celery**: Distributed task queueing for asynchronous repository processing.
- **Docker SDK for Python**: Orchestrates the secure execution sandboxes.
- **Python AST**: Analyzes logical code boundaries for semantic chunking.

### Frontend & UI
- **React.js**: Glassmorphism web interface for real-time refactoring and batch tracking.
- **Monaco Editor**: VS Code's internal engine for side-by-side syntax-highlighted diff reviews.
- **Recursive Polling Hooks**: Custom React architecture utilizing `useRef` locks to prevent memory leaks and ghost intervals during backend polling.

## Installation & Setup

### Prerequisites
- Python 3.10+ and Node.js 18+ installed.
- Docker Desktop installed and running on your host machine.
- Redis server running locally (Port 6379).
- Ollama installed locally.

### Step-by-Step Initialization

1. **Clone the Repository**:
   ```bash
   git clone [https://github.com/your-username/prism-refactor-agent.git](https://github.com/your-username/prism-refactor-agent.git)
   cd prism-refactor-agent

2. **Download the Local LLM:**
      Bash
      ollama pull qwen2.5-coder:7b


3. **Pull the Docker Sandbox Image:**
      Bash
      docker pull python:3.10-slim


4. **Start the Microservices (Requires Three Terminals):**

    #Terminal 1 (Start the FastAPI Backend):
      Bash
      cd backend
      pip install -r requirements.txt
      uvicorn main:app --reload --port 8000

   #Terminal 2 (Start the Celery Workers):
      Bash
      cd backend
      python -m celery -A worker worker --loglevel=info --pool=solo

   #Terminal 3 (Start the React Frontend):
      Bash
      cd frontend
      npm install
      npm run dev


**Usage Guide (UI & Batch)**
1. The Web UI (React + Monaco)
Navigate to http://localhost:5173. Paste your inefficient or broken legacy code into the editor, select the target translation language, and click Auto-Refactor File. Watch the live terminal console as the agent writes tests, executes the sandbox, and heals runtime errors.

2. Repository Batch Processing
Click Upload .zip Repo to ingest entire legacy codebases. The FastAPI layer will extract the files, map the extensions, and distribute the refactoring workload across background Celery workers. The React UI will display a live progress bar, logging perfectly verified files to your workspace without blocking your local machine.

Developed by Shivansh Rastogi 
(B.Tech Artificial Intelligence and Machine Learning)