```go
package main

import (
	"io/ioutil"
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
```