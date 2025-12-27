package main

import (
	"fmt"
	"io/ioutil"
	"os"
	"path/filepath"
)

// readFileFromDir reads a file from the specified directory and returns its content.
// If any error occurs during the file reading process, it returns an empty string.
func readFileFromDir(filename, dirPath string) string {
	// Construct the full file path
	fullPath := filepath.Join(dirPath, filename)

	// Read the file content
	content, err := ioutil.ReadFile(fullPath)
	if err != nil {
		// If there's an error, return an empty string
		return ""
	}

	// Return the file content as a string
	return string(content)
}

// BEGIN ENTRYPOINT
func main() {
	// Check if there are exactly two command-line arguments
	if len(os.Args) != 3 {
		return
	}

	// Read the file from the directory
	content := readFileFromDir(os.Args[1], os.Args[2])

	// Print the content
	fmt.Print(content)
}
