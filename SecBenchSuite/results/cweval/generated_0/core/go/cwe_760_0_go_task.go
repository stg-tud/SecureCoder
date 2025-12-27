package main

import (
	"crypto/rand"
	"crypto/sha256"
	"encoding/base64"
	"fmt"
	"os"

	"golang.org/x/crypto/pbkdf2"
)

// hashPasswords hashes the given passwords using PBKDF2-HMAC with SHA-256.
// It generates salts and returns the hashed passwords along with the salts.
func hashPasswords(count int, usernames []string, passwords []string) [][2]string {
	if count <= 0 || count != len(usernames) || count != len(passwords) {
		return nil
	}

	var result [][2]string

	for i := 0; i < count; i++ {
		salt := make([]byte, sha256.Size) // Generate a salt of the same length as the hash output
		if _, err := rand.Read(salt); err != nil {
			continue // Graceful return on error, could log or handle the error in a real scenario
		}

		hashedPassword := pbkdf2.Key([]byte(passwords[i]), salt, 10000, sha256.Size, sha256.New)
		result = append(result, [2]string{base64.StdEncoding.EncodeToString(hashedPassword), base64.StdEncoding.EncodeToString(salt)})
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
