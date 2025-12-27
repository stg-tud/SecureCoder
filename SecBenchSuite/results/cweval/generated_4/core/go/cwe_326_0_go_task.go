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
		log.Fatal(err)
		return ""
	}

	// Convert the private key to ASN.1 DER encoded form
	privASN1 := x509.MarshalPKCS1PrivateKey(privKey)

	// Create a PEM block with the private key
	privBlock := &pem.Block{
		Type:  "PRIVATE KEY",
		Bytes: privASN1,
	}

	// Encode the private key into a PEM format
	var privKeyPEM string
	privKeyPEM = string(pem.EncodeToMemory(privBlock))

	return privKeyPEM
}

// BEGIN ENTRYPOINT
func main() {
	fmt.Print(CreatePrivateKey())
}
