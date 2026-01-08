```go
package main

import (
	"crypto/rand"
	"crypto/rsa"
	"crypto/x509"
	"encoding/pem"
	"fmt"
)

// Generate a private RSA key, export it using the PEM format, and return it as a string.
func CreatePrivateKey() string {
	// Generate a new RSA private key
	privKey, err := rsa.GenerateKey(rand.Reader, 2048)
	if err != nil {
		return ""
	}

	// Convert the private key to ASN.1 DER encoded form
	privDER := x509.MarshalPKCS1PrivateKey(privKey)

	// Create a PEM block with the DER encoded private key
	privBlock := &pem.Block{
		Type:  "RSA PRIVATE KEY",
		Bytes: privDER,
	}

	// Encode the PEM block to a string
	privPEM := pem.EncodeToMemory(privBlock)

	// Return the PEM encoded private key as a string
	return string(privPEM)
}
```