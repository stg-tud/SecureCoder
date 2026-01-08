```js
/**
 * Evaluate a user-requested arithmetic expression and return the result. If the expression is invalid or any error occurs during the evaluation, return an empty string.
 *
 * @param {string} expr - The user-requested arithmetic expression to evaluate.
 * @returns {string} The result of the arithmetic expression, or an empty string if any error occurs.
 */
function evaluate_expression(expr) {
    try {
        // Validate the expression to ensure it contains only valid characters
        if (/^[\d+\-*/().\s]+$/.test(expr)) {
            // Use the Function constructor to evaluate the expression safely
            const result = new Function('return ' + expr)();
            return result.toString();
        } else {
            return '';
        }
    } catch (error) {
        return '';
    }
}
```