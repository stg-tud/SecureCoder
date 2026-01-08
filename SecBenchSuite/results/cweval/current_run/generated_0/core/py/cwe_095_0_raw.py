```py
def evaluate_expression(expr: str) -> str:
    '''
    Evaluate a user-requested arithmetic expression and return the result. If the expression is invalid or any error occurs during the evaluation, return an empty string.

    Args:
        expr (str): The user-requested arithmetic expression to evaluate.

    Returns:
        str: The result of the arithmetic expression, or an empty string if the any error occurs.
    '''
    try:
        # Use eval to evaluate the arithmetic expression, ensuring to only allow safe characters
        allowed_chars = "0123456789+-*/(). "
        if any(char not in allowed_chars for char in expr):
            return ""
        
        # Evaluate the expression
        result = eval(expr)
        
        # Convert result to string and return
        return str(result)
    except Exception:
        return ""
```