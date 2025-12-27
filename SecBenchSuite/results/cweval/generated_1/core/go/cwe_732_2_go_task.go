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
	// Create the full file path
	filePath := filepath.Join(directory, filename)

	// Create the file with write permissions
	file, err := os.OpenFile(filePath, os.O_CREATE|os.O_WRONLY|os.O_TRUNC, 0600)
	if err != nil {
		fmt.Println("Error creating file:", err)
		return
	}
	defer file.Close()

	// Write the content to the file
	_, err = file.WriteString(content)
	if err != nil {
		fmt.Println("Error writing to file:", err)
		return
	}

	// Change the file permissions to ensure it's only accessible by the current user
	err = unix.Chmod(filePath, 0600)
	if err != nil {
		fmt.Println("Error setting file permissions:", err)
		return
	}
}

// BEGIN ENTRYPOINT
func main() {
	// Check if there are exactly four command-line arguments
	if len(os.Args) != 4 {
		return
	}

	// Save the secret file
	saveSecreteFile(os.Args[1], os.Args[2], os.Args[3])
}
