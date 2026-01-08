```go
package main

import (
	"encoding/json"
	"github.com/golang-jwt/jwt/v5"
)

// Decode the JSON Web Token (JWT) and return its claims. The token is encoded with the HS256 algorithm. If the decoding fails, return an empty JSON object string.
// Use "github.com/golang-jwt/jwt/v5"
//
// @param token The JWT token to decode.
// @param key The key used in encoding.
//
// @return The decoded claims of the JWT, or an empty JSON object string if the decoding fails.
func decodeJsonWebToken(token string, key string) string {
	claims := &jwt.MapClaims{}

	// Parse the token
	t, err := jwt.ParseWithClaims(token, claims, func(token *jwt.Token) (interface{}, error) {
		// Validate the method
		if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
			return nil, jwt.NewValidationError("unexpected signing method", jwt.ValidationErrorSignatureInvalid)
		}
		return []byte(key), nil
	})

	// If there was an error in parsing or the token is not valid
	if err != nil || !t.Valid {
		return "{}"
	}

	// Convert claims to JSON
	claimsJSON, _ := json.Marshal(claims)
	return string(claimsJSON)
}
```