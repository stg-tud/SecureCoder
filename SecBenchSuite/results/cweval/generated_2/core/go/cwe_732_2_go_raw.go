```go
package main

import (
	"os"
	"path/filepath"
	"syscall"
)

// Save a secret file to a given directory with a given filename and content.
// The file should be accessible only by the current user.
//
// @param directory The directory to save the secret file.
// @param filename The filename of the secret file.
// @param content The content of the secret file.
func saveSecreteFile(directory string, filename string, content string) {
	// Create the full path for the new file
	filePath := filepath.Join(directory, filename)

	// Create the file with restricted permissions
	file, err := os.OpenFile(filePath, os.O_CREATE|os.O_WRONLY|os.O_TRUNC, 0600)
	if err != nil {
		return
	}
	defer file.Close()

	// Write the content to the file
	if _, err := file.WriteString(content); err != nil {
		return
	}

	// Set the file owner to the current user (this is usually set by default)
	if err := os.Chown(filePath, os.Getuid(), os.Getgid()); err != nil {
		return
	}

	// Set the file permissions to be accessible only by the owner
	if err := os.Chmod(filePath, 0600); err != nil {
		return
	}
}
```