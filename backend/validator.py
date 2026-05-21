import ast


def check_syntax(code: str, language: str = "python"):
    if not isinstance(code, str):
        return False, "optimized_code must be a string."

    if not code.strip():
        return False, "Generated code is empty."

    try:
        ast.parse(code)
    except SyntaxError as e:
        return False, f"Syntax Error: {e.msg} at line {e.lineno}"

    if len(code.splitlines()) < 2:
        return False, "Code appears truncated."

    return True, "Valid"
