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
func encryptData(key []byte, data []byte) (encryptedData []byte, iv []byte, aesKey []byte, err error) {
	if len(key) < 16 {
		return nil, nil, nil, errors.New("key must be at least 16 bytes")
	}

	// Use only the first 16, 24, or 32 bytes of the key for AES
	var keyLength int
	switch len(key) {
	case 16:
		keyLength = 16
	case 24:
		keyLength = 24
	case 32:
		keyLength = 32
	default:
		keyLength = 16 // default to 16 bytes if key is longer than 32 bytes
	}

	aesKey = key[:keyLength]

	// Create a new AES cipher
	block, err := aes.NewCipher(aesKey)
	if err != nil {
		return nil, nil, nil, err
	}

	// Create a new IV (initialization vector)
	iv = make([]byte, aes.BlockSize)
	if _, err := io.ReadFull(rand.Reader, iv); err != nil {
		return nil, nil, nil, err
	}

	// Pad the data to be a multiple of the block size
	paddedData := pad(data, aes.BlockSize)

	// Encrypt the data using the cipher
	mode := cipher.NewCBCEncrypter(block, iv)
	encryptedData = make([]byte, len(paddedData))
	mode.CryptBlocks(encryptedData, paddedData)

	return encryptedData, iv, aesKey, nil
}

// pad adds padding to the data to make its length a multiple of blockSize.
func pad(data []byte, blockSize int) []byte {
	padding := blockSize - len(data)%blockSize
	padText := byte(padding)
	paddedData := append(data, bytes.Repeat([]byte{padText}, padding)...)
	return paddedData
}
```