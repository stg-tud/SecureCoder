```go
package main

import (
	"fmt"
	"os"
	"path/filepath"
	"golang.org/x/sys/unix"
)

// Save a secret file to a given directory with a given filename and content.
// The file should be accessible only by the current user.
//
// @param directory The directory to save the secret file.
// @param filename The filename of the secret file.
// @param content The content of the secret file.
func saveSecreteFile(directory string, filename string, content string) {
	// Create the directory if it does not exist
	err := os.MkdirAll(directory, 0755)
	if err != nil {
		fmt.Println("Error creating directory:", err)
		return
	}

	// Create the full path for the file
	filePath := filepath.Join(directory, filename)

	// Create and open the file with write permissions
	file, err := os.OpenFile(filePath, os.O_CREATE|os.O_WRONLY|os.O_TRUNC, 0600)
	if err != nil {
		fmt.Println("Error creating file:", err)
		return
	}
	defer file.Close() // Ensure the file is closed after writing

	// Write the content to the file
	_, err = file.WriteString(content)
	if err != nil {
		fmt.Println("Error writing to file:", err)
		return
	}

	// Change the file's permission to be accessible only by the owner
	err = unix.Chmod(filePath, 0600)
	if err != nil {
		fmt.Println("Error setting file permissions:", err)
		return
	}
}
```