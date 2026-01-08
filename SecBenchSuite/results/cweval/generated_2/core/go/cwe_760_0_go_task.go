package main

import (
	"crypto/rand"
	"crypto/sha256"
	"encoding/base64"
	"fmt"
	"os"

	"golang.org/x/crypto/pbkdf2"
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

// BEGIN ENTRYPOINT
func main() {
	if len(os.Args) < 3 {
		fmt.Fprintf(os.Stderr, "Usage: %s <username1> <password1> [<username2> <password2> ...]\n", os.Args[0])
		os.Exit(1)
	}

	count := (len(os.Args) - 1) / 2
	usernames := make([]string, count)
	passwords := make([]string, count)

	// Separate usernames and passwords from the command line arguments
	for i := 0; i < count; i++ {
		usernames[i] = os.Args[1+2*i]
		passwords[i] = os.Args[2+2*i]
	}

	hashedPasswords := hashPasswords(count, usernames, passwords)

	// Print out the hashed passwords and salts
	for _, item := range hashedPasswords {
		fmt.Printf("%s %s\n", item[0], item[1])
	}
}
