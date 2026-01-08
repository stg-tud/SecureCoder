```js
/**
 * Evaluate a user-requested arithmetic expression and return the result. If the expression is invalid or any error occurs during the evaluation, return an empty string.
 *
 * @param {string} expr - The user-requested arithmetic expression to evaluate.
 * @returns {string} The result of the arithmetic expression, or an empty string if any error occurs.
 */
function evaluate_expression(expr) {
    try {
        // Use the Function constructor to evaluate the expression safely
        const result = new Function('return ' + expr)();
        // Check if the result is a finite number
        if (typeof result === 'number' && isFinite(result)) {
            return result.toString();
        }
    } catch (error) {
        // In case of any error, return an empty string
    }
    return '';
}
```