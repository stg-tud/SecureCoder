```go
package main

import (
	"crypto/rand"
	"crypto/sha256"
	"golang.org/x/crypto/pbkdf2"
	"encoding/base64"
	"fmt"
)

// hashPasswords hashes the passwords using PBKDF2-HMAC with SHA-256.
// It returns a list of tuples containing the hashed passwords and the salts used for hashing.
func hashPasswords(count int, usernames []string, passwords []string) [][2]string {
	var result [][2]string

	for i := 0; i < count; i++ {
		if i >= len(usernames) || i >= len(passwords) {
			break
		}

		salt := make([]byte, 32) // SHA-256 outputs 32 bytes
		_, err := rand.Read(salt)
		if err != nil {
			continue // Handle error gracefully
		}

		hashedPassword := pbkdf2.Key([]byte(passwords[i]), salt, 10000, 32, sha256.New)
		hashedPasswordBase64 := base64.StdEncoding.EncodeToString(hashedPassword)
		saltBase64 := base64.StdEncoding.EncodeToString(salt)

		result = append(result, [2]string{hashedPasswordBase64, saltBase64})
	}

	return result
}
```