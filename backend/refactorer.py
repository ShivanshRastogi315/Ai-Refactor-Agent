import re

def rename_variable(code, old_name, new_name):
    """
    A simple action: Renames a variable. 
    (In a real AST agent, this would check scope, but this is a starter version).
    """
    # Simple regex replacement (Improve this logic later for safety)
    # This acts as the "Effect" mentioned in your planner [cite: 99]
    new_code = re.sub(r'\b' + re.escape(old_name) + r'\b', new_name, code)
    return new_code

def remove_comments(code):
    """
    Action: Cleans up code by removing comments to reduce LOC.
    """
    # Removes // comments
    code = re.sub(r'//.*', '', code)
    # Removes /* */ comments
    code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
    return code

# List of available moves the agent can try
AVAILABLE_MOVES = [
    ("remove_comments", remove_comments),
    # You can add more complex moves here later like "extract_method"
]