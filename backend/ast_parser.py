import ast

class CodeAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.features = set()

    def visit_For(self, node):
        self.features.add("loop optimization and list comprehensions")
        self.generic_visit(node)

    def visit_Try(self, node):
        self.features.add("error exception handling")
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        self.features.add("naming conventions and type hints")
        self.generic_visit(node)
        
    def visit_Import(self, node):
        self.features.add("import management")
        self.generic_visit(node)

def extract_code_features(code: str) -> list[str]:
    """Parses code into an AST and extracts structural features for RAG querying."""
    try:
        tree = ast.parse(code)
        analyzer = CodeAnalyzer()
        analyzer.visit(tree)
        return list(analyzer.features)
    except SyntaxError:
        # If the code is completely broken syntactically, fallback to general rules
        return ["syntax correction", "general clean code best practices"]