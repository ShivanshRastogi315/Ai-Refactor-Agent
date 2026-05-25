import ast

def semantic_chunking(source_code: str) -> list[str]:
    """
    Parses Python code into an AST and extracts logical top-level blocks.
    Prevents LLM context window overflow on massive enterprise files.
    """
    try:
        tree = ast.parse(source_code)
    except SyntaxError:
        # If the original code is completely broken syntactically, 
        # return it as a single chunk to let the LLM attempt a global fix.
        return [source_code]

    chunks = []
    current_chunk = []

    for node in tree.body:
        # Extract the exact string representation of this node
        node_code = ast.get_source_segment(source_code, node)
        if not node_code:
            continue

        # If the node is a large block (Class or Function), it gets its own chunk
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            # Flush any small statements/imports we've collected first
            if current_chunk:
                chunks.append("\n".join(current_chunk))
                current_chunk = []
            
            chunks.append(node_code)
        else:
            # Group smaller statements like imports and global variables together
            current_chunk.append(node_code)

    # Flush the remaining code
    if current_chunk:
        chunks.append("\n".join(current_chunk))

    return chunks