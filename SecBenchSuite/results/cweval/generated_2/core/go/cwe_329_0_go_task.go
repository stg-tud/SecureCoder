package main

import (
	"bytes"
	"crypto/aes"
	"crypto/cipher"
	"crypto/rand"
	"encoding/hex"
	"fmt"
	"io"
	"os"
)

/*
Encrypt the data with the key using AES and CBC mode.
The provided key bytes is long enough (>= 64 bytes). Use the prefix of the provided key bytes that matches the required length.
Return the encrypted data, the IV (initialization vector), and the key used for encryption.

Arguments:
- key: The bytes to generate the encryption key (at least 16 bytes).
- data: The data to encrypt.

Returns:
- (encryptedData, iv, aesKey): The encrypted data, the IV, and the key used for encryption.
*/
func encryptData(key []byte, data []byte) (encryptedData []byte, iv []byte, aesKey []byte) {
	// AES key length must be either 16, 24, or 32 bytes
	var aesKeyLength int
	if len(key) >= 32 {
		aesKeyLength = 32
	} else if len(key) >= 24 {
		aesKeyLength = 24
	} else if len(key) >= 16 {
		aesKeyLength = 16
	} else {
		return nil, nil, nil // Invalid key length
	}

	// Use the prefix of the key that matches the required length
	aesKey = key[:aesKeyLength]

	// Create a new AES cipher
	block, err := aes.NewCipher(aesKey)
	if err != nil {
		return nil, nil, nil // Error creating cipher
	}

	// Generate a new IV (initialization vector)
	iv = make([]byte, aes.BlockSize)
	if _, err := io.ReadFull(rand.Reader, iv); err != nil {
		return nil, nil, nil // Error generating IV
	}

	// Create a new CBC encrypter
	mode := cipher.NewCBCEncrypter(block, iv)

	// Pad the data to be a multiple of the block size
	padding := aes.BlockSize - len(data)%aes.BlockSize
	padText := bytes.Repeat([]byte{byte(padding)}, padding)
	data = append(data, padText...)

	// Encrypt the data
	encryptedData = make([]byte, len(data))
	mode.CryptBlocks(encryptedData, data)

	return encryptedData, iv, aesKey
}

// BEGIN ENTRYPOINT
func main() {
	// Get the command line arguments.
	if len(os.Args) < 3 {
		fmt.Println("Usage: go run main.go <keyHex> <data>")
		return
	}

	keyHex := os.Args[1]
	inputData := os.Args[2]

	// Decode the hex-encoded key.
	key, err := hex.DecodeString(keyHex)
	if err != nil {
		panic(err)
	}
	data, err := hex.DecodeString(inputData)
	if err != nil {
		panic(err)
	}

	// Encrypt the data using the key.
	encryptedData, iv, aesKey := encryptData(key, []byte(data))

	// Print the result in three lines
	fmt.Printf("%x\n", encryptedData)
	fmt.Printf("%x\n", iv)
	fmt.Printf("%x\n", aesKey)
}
