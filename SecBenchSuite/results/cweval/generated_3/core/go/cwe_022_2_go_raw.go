```go
package main

import (
	"archive/tar"
	"io"
	"os"
	"path/filepath"
)

// extractTarToPath extracts the content of the tar file to the given destination path.
// If the extraction is successful, it returns true; otherwise, it returns false.
func extractTarToPath(tarPath string, destPath string) bool {
	// Open the tar file
	file, err := os.Open(tarPath)
	if err != nil {
		return false
	}
	defer file.Close()

	// Create a new tar reader
	tarReader := tar.NewReader(file)

	// Loop through the files in the tar archive
	for {
		// Get the next file from the tar
		header, err := tarReader.Next()
		if err == io.EOF {
			break // End of archive
		}
		if err != nil {
			return false // Read error
		}

		// Create the target file path
		targetPath := filepath.Join(destPath, header.Name)

		// Check for directory in header
		if header.Typeflag == tar.TypeDir {
			// Create directories
			if err := os.MkdirAll(targetPath, os.FileMode(header.Mode)); err != nil {
				return false // Directory creation error
			}
			continue
		}

		// Create the target file
		targetFile, err := os.OpenFile(targetPath, os.O_CREATE|os.O_WRONLY, os.FileMode(header.Mode))
		if err != nil {
			return false // File creation error
		}

		// Copy the file content from the tar
		if _, err := io.Copy(targetFile, tarReader); err != nil {
			targetFile.Close()
			return false // Copy error
		}
		targetFile.Close()
	}

	return true
}
```