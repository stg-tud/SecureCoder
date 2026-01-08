```go
package main

import (
	"fmt"
	"io/ioutil"
	"path/filepath"
)

// readFileFromDir reads the contents of a file from the specified directory path.
// It returns the content of the file if it exists and is accessible; otherwise, it returns an empty string.
func readFileFromDir(filename, dirPath string) string {
	// Construct the full file path
	filePath := filepath.Join(dirPath, filename)

	// Read the file content
	content, err := ioutil.ReadFile(filePath)
	if err != nil {
		// If any error occurs, return an empty string
		return ""
	}

	// Return the file content as a string
	return string(content)
}
```