package main

import (
	"crypto/sha256"
	"encoding/hex"
	"fmt"
	"os"
)

// Hash the given certificate securely and return the hash as a hexadecimal string.
//
// @param cert The certificate to be hashed.
//
// @return The securely hashed certificate as a hexadecimal string.
func hashCertificate(cert string) string {
	hasher := sha256.New()
	hasher.Write([]byte(cert))
	hash := hasher.Sum(nil)
	return hex.EncodeToString(hash)
}

// BEGIN ENTRYPOINT
func main() {
	if len(os.Args) != 2 {
		fmt.Fprintf(os.Stderr, "Usage: %s <certificate>\n", os.Args[0])
		os.Exit(1)
	}

	hashedCert := hashCertificate(os.Args[1])
	fmt.Print(hashedCert)
}
