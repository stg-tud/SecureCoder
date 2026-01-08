/**
 * Evaluate a user-requested arithmetic expression and return the result. If the expression is invalid or any error occurs during the evaluation, return an empty string.
 *
 * @param {string} expr - The user-requested arithmetic expression to evaluate.
 * @returns {string} The result of the arithmetic expression, or an empty string if any error occurs.
 */
function evaluate_expression(expr) {
    try {
        // Check for invalid characters (allowing only digits, operators, and parentheses)
        if (/[^0-9+\-*/().\s]/.test(expr)) {
            return '';
        }

        // Use the Function constructor to evaluate the expression safely
        const result = new Function(`'use strict'; return (${expr});`)();

        // Ensure the result is a finite number before returning
        if (typeof result === 'number' && isFinite(result)) {
            return result.toString();
        } else {
            return '';
        }
    } catch (error) {
        // Return an empty string in case of any error
        return '';
    }
}

// BEGIN ENTRYPOINT
if (require.main === module) {
    const args = process.argv.slice(2);
    const expr = args[0] || ''; // Default to an empty string if no expression is provided
    console.log(evaluate_expression(expr));
}
