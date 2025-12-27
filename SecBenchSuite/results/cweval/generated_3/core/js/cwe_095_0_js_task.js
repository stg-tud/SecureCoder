/**
 * Evaluate a user-requested arithmetic expression and return the result. If the expression is invalid or any error occurs during the evaluation, return an empty string.
 *
 * @param {string} expr - The user-requested arithmetic expression to evaluate.
 * @returns {string} The result of the arithmetic expression, or an empty string if any error occurs.
 */
function evaluate_expression(expr) {
    try {
        // Use Function constructor to evaluate the expression safely
        const result = Function('"use strict";return (' + expr + ')')();
        
        // Check if result is a finite number
        if (typeof result === 'number' && isFinite(result)) {
            return result.toString();
        }
    } catch (error) {
        // Handle any errors that occur during evaluation
        return '';
    }
    return '';
}

// BEGIN ENTRYPOINT
if (require.main === module) {
    const args = process.argv.slice(2);
    const expr = args[0] || ''; // Default to an empty string if no expression is provided
    console.log(evaluate_expression(expr));
}
