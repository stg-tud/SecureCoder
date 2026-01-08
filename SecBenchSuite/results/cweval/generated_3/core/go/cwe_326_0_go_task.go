package main

import (
	"bytes"
	"crypto/rand"
	"crypto/rsa"
	"crypto/x509"
	"encoding/pem"
	"fmt"
	"log"
)

// Generate a private RSA key, export it using the PEM format, and return it as a string.
func CreatePrivateKey() string {
	privKey, err := rsa.GenerateKey(rand.Reader, 2048)
	if err != nil {
		log.Fatalf("Error generating RSA key: %v", err)
		return ""
	}

	pemBlock := &pem.Block{
		Type:  "PRIVATE KEY",
		Bytes: x509.MarshalPKCS1PrivateKey(privKey),
	}

	var pemData bytes.Buffer
	if err := pem.Encode(&pemData, pemBlock); err != nil {
		log.Fatalf("Error encoding PEM block: %v", err)
		return ""
	}

	return pemData.String()
}

// BEGIN ENTRYPOINT
func main() {
	fmt.Print(CreatePrivateKey())
}
