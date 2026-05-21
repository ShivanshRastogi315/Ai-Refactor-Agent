import os
import chromadb
from chromadb.utils import embedding_functions
from backend.ast_parser import extract_code_features

class KnowledgeBase:
    def __init__(self):
        self.standards_file = "data/coding_standards.txt"
        
        # Initialize ChromaDB persistent client
        os.makedirs("chroma_db", exist_ok=True)
        self.client = chromadb.PersistentClient(path="./chroma_db")
        
        # Use a lightweight sentence transformer for fast local embeddings
        self.embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
        
        # Reset collection to ensure fresh data loads when we update the text file
        try:
            self.client.delete_collection("coding_standards")
        except Exception:
            pass
            
        self.collection = self.client.create_collection(
            name="coding_standards", 
            embedding_function=self.embed_fn
        )
        self._populate_db()

    def _populate_db(self):
        if not os.path.exists(self.standards_file):
            print(f"Warning: Standards file {self.standards_file} not found.")
            return

        with open(self.standards_file, "r") as f:
            # Each line in the text file becomes a separate vector chunk
            rules = [line.strip() for line in f.readlines() if line.strip()]
        
        if rules:
            self.collection.add(
                documents=rules,
                ids=[f"rule_{i}" for i in range(len(rules))]
            )

    def retrieve(self, code: str) -> str:
        # 1. Analyze code to find out what it does
        features = extract_code_features(code)
        
        # 2. Build a specific semantic search query based on the code's structure
        if not features:
            query = "General python clean code formatting and best practices"
        else:
            query = " ".join(features)

        # 3. Retrieve the top 3 most relevant coding standards from the DB
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=3
            )
            retrieved_rules = results['documents'][0]
            return "\n".join([f"- {rule}" for rule in retrieved_rules])
        except Exception as e:
            return f"Standard industry coding practices. (RAG Error: {e})"

knowledge_base = KnowledgeBase()