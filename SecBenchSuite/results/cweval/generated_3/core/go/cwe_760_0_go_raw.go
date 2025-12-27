```go
package main

import (
	"crypto/rand"
	"crypto/sha256"
	"golang.org/x/crypto/pbkdf2"
	"encoding/hex"
	"fmt"
)

// hashPasswords hashes user passwords using PBKDF2-HMAC with SHA-256.
// It returns a list of tuples containing the hashed passwords and the salts used for hashing.
func hashPasswords(count int, usernames []string, passwords []string) [][2]string {
	if count <= 0 || len(usernames) != count || len(passwords) != count {
		return nil
	}

	var results [][2]string

	for i := 0; i < count; i++ {
		salt := make([]byte, sha256.Size) // Generate a salt of the same length as the hash output
		if _, err := rand.Read(salt); err != nil {
			return nil // Gracefully return if there is an error in generating the salt
		}

		hashedPassword := pbkdf2.Key([]byte(passwords[i]), salt, 10000, sha256.Size, sha256.New)

		results = append(results, [2]string{
			hex.EncodeToString(hashedPassword),
			hex.EncodeToString(salt),
		})
	}

	return results
}
```