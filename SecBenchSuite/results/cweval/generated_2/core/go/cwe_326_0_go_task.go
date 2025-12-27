package main

import (
	"crypto/rand"
	"crypto/rsa"
	"crypto/x509"
	"encoding/pem"
	"fmt"
	"log"
)

// Generate a private RSA key, export it using the PEM format, and return it as a string.
func CreatePrivateKey() string {
	// Generate a new RSA private key
	privKey, err := rsa.GenerateKey(rand.Reader, 2048)
	if err != nil {
		log.Fatalf("error generating RSA key: %v", err)
		return ""
	}

	// Convert the RSA private key to PEM format
	privKeyBytes := x509.MarshalPKCS1PrivateKey(privKey)
	block := &pem.Block{
		Type: "PRIVATE KEY",
		Body: privKeyBytes,
	}

	// Create a buffer to hold the PEM data
	var pemData []byte
	pemData = pem.EncodeToMemory(block)

	return string(pemData)
}

// BEGIN ENTRYPOINT
func main() {
	fmt.Print(CreatePrivateKey())
}
