```go
package main

import (
	"crypto/rand"
	"crypto/sha256"
	"golang.org/x/crypto/pbkdf2"
	"encoding/base64"
	"fmt"
)

// hashPasswords hashes the provided passwords using PBKDF2-HMAC with SHA-256.
// It generates a random salt for each password and returns a list of tuples
// containing the hashed passwords and the salts used for hashing.
func hashPasswords(count int, usernames []string, passwords []string) [][2]string {
	var result [][2]string

	for i := 0; i < count; i++ {
		if i >= len(usernames) || i >= len(passwords) {
			break // Avoid index out of range if count exceeds available usernames or passwords
		}

		salt := make([]byte, 32) // SHA-256 produces a 32-byte hash
		if _, err := rand.Read(salt); err != nil {
			// Handle error (In production, consider logging the error)
			continue
		}

		hash := pbkdf2.Key([]byte(passwords[i]), salt, 10000, 32, sha256.New)
		hashedPassword := base64.StdEncoding.EncodeToString(hash)
		saltEncoded := base64.StdEncoding.EncodeToString(salt)

		result = append(result, [2]string{hashedPassword, saltEncoded})
	}

	return result
}
```