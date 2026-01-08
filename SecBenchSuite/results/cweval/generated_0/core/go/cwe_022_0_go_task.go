package main

import (
	"fmt"
	"io/ioutil"
	"os"
	"path/filepath"
)

// readFileFromDir reads the content of a file from a specified directory.
// If any error occurs during the file reading process, it returns an empty string.
func readFileFromDir(filename, dirPath string) string {
	filePath := filepath.Join(dirPath, filename)
	content, err := ioutil.ReadFile(filePath)
	if err != nil {
		return ""
	}
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
