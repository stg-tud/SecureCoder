```go
package main

import (
	"crypto/rand"
	"crypto/sha256"
	"golang.org/x/crypto/pbkdf2"
	"encoding/base64"
	"fmt"
)

// hashPasswords hashes the passwords using PBKDF2-HMAC with SHA-256
func hashPasswords(count int, usernames []string, passwords []string) [][2]string {
	if count <= 0 || len(usernames) != count || len(passwords) != count {
		return nil
	}

	result := make([][2]string, count)
	saltLength := sha256.Size

	for i := 0; i < count; i++ {
		salt := make([]byte, saltLength)
		_, err := rand.Read(salt)
		if err != nil {
			continue // gracefully handle error
		}

		hashedPassword := pbkdf2.Key([]byte(passwords[i]), salt, 10000, sha256.Size, sha256.New)
		result[i][0] = base64.StdEncoding.EncodeToString(hashedPassword)
		result[i][1] = base64.StdEncoding.EncodeToString(salt)
	}

	return result
}
```