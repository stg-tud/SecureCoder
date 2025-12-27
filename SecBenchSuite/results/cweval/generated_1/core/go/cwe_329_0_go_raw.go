```go
package main

import (
	"crypto/aes"
	"crypto/cipher"
	"crypto/rand"
	"errors"
	"io"
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
	if len(key) < 16 {
		return nil, nil, nil // Key must be at least 16 bytes for AES
	}

	// Use only the first 16 bytes of the key for AES-128
	aesKey = key[:16]

	// Create a new AES cipher block
	block, err := aes.NewCipher(aesKey)
	if err != nil {
		return nil, nil, nil
	}

	// Generate a new IV
	iv = make([]byte, aes.BlockSize)
	if _, err := io.ReadFull(rand.Reader, iv); err != nil {
		return nil, nil, nil
	}

	// Pad data to be a multiple of the block size
	padding := aes.BlockSize - len(data)%aes.BlockSize
	padtext := bytes.Repeat([]byte{byte(padding)}, padding)
	data = append(data, padtext...)

	// Encrypt the data using CBC mode
	mode := cipher.NewCBCEncrypter(block, iv)
	encryptedData = make([]byte, len(data))
	mode.CryptBlocks(encryptedData, data)

	return encryptedData, iv, aesKey
}
```