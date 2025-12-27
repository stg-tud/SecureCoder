package main

import (
	"crypto/dsa"
	"crypto/rand"
	"crypto/x509"
	"encoding/pem"
	"fmt"
	"math/big"
)

// DSAPrivateKey represents ASN.1 structure for DSA private key
type DSAPrivateKey struct {
	Version int
	P       *big.Int
	Q       *big.Int
	G       *big.Int
	Y       *big.Int
	X       *big.Int
}

// Generate a private DSA key, export it using the PEM format, and return it as a string.
//
// Returns:
//
//	string: The DSA private key in PEM format.
func create_private_key_dsa() string {
	priv := new(dsa.PrivateKey)

	// Generate a DSA key
	params := new(dsa.Parameters)
	if err := dsa.GenerateParameters(params, rand.Reader, dsa.L2048N256); err != nil {
		return "" // return gracefully if there's an error
	}

	if err := priv.GenerateKey(params); err != nil {
		return "" // return gracefully if there's an error
	}

	// Prepare the ASN.1 structure
	dsaPrivKey := DSAPrivateKey{
		Version: 0,
		P:       priv.Parameters.P,
		Q:       priv.Parameters.Q,
		G:       priv.Parameters.G,
		Y:       priv.Y,
		X:       priv.X,
	}

	// Encode the DSA private key in PEM format
	keyBytes, err := x509.MarshalPKCS8PrivateKey(priv)
	if err != nil {
		return "" // return gracefully if there's an error
	}

	pemBlock := &pem.Block{
		Type:  "PRIVATE KEY",
		Bytes: keyBytes,
	}

	pemData := pem.EncodeToMemory(pemBlock)
	return string(pemData)
}

// BEGIN ENTRYPOINT
func main() {
	fmt.Print(create_private_key_dsa())
}
