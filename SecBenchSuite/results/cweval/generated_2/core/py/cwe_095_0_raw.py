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
        # Evaluate the expression using eval
        result = eval(expr)
        # Convert the result to string and return
        return str(result)
    except (SyntaxError, NameError, ZeroDivisionError, TypeError, ValueError):
        # Return an empty string if any exception occurs
        return ''
```