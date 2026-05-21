# Autonomous Code Refactoring Agent

An enterprise-grade, fully local AI-powered refactoring system designed to transform inefficient, syntactically broken, or poorly structured code into optimized, production-ready implementations. Moving beyond standard text generation, this agent employs a Reflection Architecture, utilizing Docker-based sandboxed execution to verify its own code, AST-driven Retrieval-Augmented Generation (RAG) to enforce strict coding standards, and a decoupled FastAPI backend for seamless CI/CD pipeline integration.

## Abstract

Writing code is easy; maintaining clean, optimized, and scalable code is hard. Traditional static analyzers catch syntax errors but cannot refactor logic. Cloud-based LLMs can refactor logic but pose severe data privacy risks and often hallucinate variables or break existing functionality.

This project bridges that gap. By combining the local reasoning power of Qwen2.5-Coder with an isolated Docker execution sandbox, the agent acts as a senior developer. It reads the code, maps its Abstract Syntax Tree (AST), queries a vector database for organizational coding standards, runs static analysis, generates a refactored solution, and most importantly—tests its own code. If the code crashes, the agent reads the runtime error traceback and self-corrects before presenting the final output.

All of this happens entirely locally, ensuring zero data leakage.

## Key Features & Use Cases

- **Algorithmic Optimization**: Automatically identifies $O(n^2)$ bottlenecks (like nested loops) and refactors them into $O(n)$ or $O(n \log n)$ solutions using Hash Sets and optimized data structures.
- **The Reflection Loop (Self-Healing)**: Executes generated code in a secure, network-disabled Docker container. If a runtime error (e.g., IndexError, TypeError) occurs, the agent reads the traceback and attempts to fix its own mistake.
- **AST-Driven RAG Context**: Parses code into an Abstract Syntax Tree to understand its structure (e.g., detecting for loops or try/except blocks), then queries ChromaDB to inject highly specific coding standards into the LLM's prompt.
- **CI/CD Pipeline Ready**: Completely decoupled architecture allows the agent to review Pull Requests automatically via GitHub Actions, leaving no need for manual UI interaction.
- **Privacy-First**: Powered by Ollama, running 100% offline.

## Architecture & Methodology

The system operates on a highly structured, 5-stage pipeline:

1. **Static Analysis Pre-Processing (pylint)**: Before engaging the LLM, the code is passed through traditional static analyzers. This catches obvious syntax and style violations (PEP-8), saving LLM compute power for deep logical reasoning.
2. **AST Feature Extraction & RAG (ast, ChromaDB)**: The system parses the original code to extract structural features. These features are embedded via Sentence-Transformers and used to query a vector database containing the organization's specific coding standards.
3. **LLM Generation (Qwen2.5-Coder)**: The local LLM receives the original code, the static analysis report, and the dynamically retrieved coding standards, generating a mathematically and syntactically optimized solution.
4. **Sandboxed Verification (Docker)**: The newly generated code is mounted into a lightweight, ephemeral python:3.10-slim Docker container. It is executed with strict memory constraints and a timeout limit to prevent infinite loops.
5. **The Reflection Retry**: If the Docker container exits with an error code, the agent is fed the stderr traceback and given one retry to reflect on its logical failure and output a corrected script.

## Technologies Used

### Backend & Core Logic

- **FastAPI & Uvicorn**: High-performance async API routing.
- **Ollama (Qwen2.5-Coder)**: The core open-weight reasoning engine.
- **Docker SDK for Python**: Orchestrates the secure execution sandboxes.
- **Python AST**: Analyzes logical code boundaries.
- **ChromaDB & Sentence-Transformers**: Vector database and embeddings (all-MiniLM-L6-v2) for the RAG knowledge base.
- **Pylint**: Deterministic static code analysis.

### Frontend & Automation

- **Streamlit**: Interactive web interface for manual refactoring and log visualization.
- **Requests / CLI**: Command-line interface for terminal-based refactoring.
- **GitHub Actions**: CI/CD YAML pipelines for automated Pull Request reviews.

## Installation & Setup

### Prerequisites

- Python 3.10+ installed.
- Docker Desktop installed and running on your host machine.
- Ollama installed locally.

### Step-by-Step Initialization

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/your-username/auto-refactor-agent.git
   cd auto-refactor-agent
   ```

2. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Download the Local LLM**:

   ```bash
   ollama pull qwen2.5-coder:latest
   ```

4. **Pull the Docker Sandbox Image**:

   ```bash
   docker pull python:3.10-slim
   ```

5. **Start the Microservices (Requires Two Terminals)**:

   - **Terminal 1 (Start the Backend Engine)**:

	 ```bash
	 uvicorn backend.main:app --reload --port 8000
	 ```

   - **Terminal 2 (Start the Frontend UI)**:

	 ```bash
	 streamlit run app.py
	 ```

## Usage Guide (UI & CLI)

### 1. The Web UI (Streamlit)

Navigate to [http://localhost:8501](http://localhost:8501). Paste your inefficient or broken code into the editor, select the language, and click Auto-Repair & Optimize. Expand the "Agent Thought Process" toggle to watch the system run static analysis, query ChromaDB, and execute the Docker reflection loop in real-time.

### 2. The Command Line Interface (CLI)

For rapid terminal development, you can refactor local files directly. The CLI sends the file to the FastAPI backend and overwrites it with the optimized version.