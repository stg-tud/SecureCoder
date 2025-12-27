```go
package main

import (
	"crypto/rand"
	"crypto/sha256"
	"golang.org/x/crypto/pbkdf2"
	"encoding/base64"
	"fmt"
)

func hashPasswords(count int, usernames []string, passwords []string) [][2]string {
	if count <= 0 || len(usernames) != count || len(passwords) != count {
		return nil
	}

	hashes := make([][2]string, count)

	for i := 0; i < count; i++ {
		salt := make([]byte, sha256.Size)
		if _, err := rand.Read(salt); err != nil {
			return nil
		}
		hash := pbkdf2.Key([]byte(passwords[i]), salt, 10000, sha256.Size, sha256.New)
		hashes[i] = [2]string{base64.StdEncoding.EncodeToString(hash), base64.StdEncoding.EncodeToString(salt)}
	}

	return hashes
}
```