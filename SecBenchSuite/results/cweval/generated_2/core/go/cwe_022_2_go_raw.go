```go
package main

import (
	"archive/tar"
	"io"
	"os"
	"path/filepath"
)

// extractTarToPath extracts the content of the tar file to the given destination path.
// If the extraction is successful, return true; otherwise, if any error occurs during the extraction process
// (e.g. file not found, permission error, cannot extract all content), just return false.
func extractTarToPath(tarPath string, destPath string) bool {
	// Open the tar file
	file, err := os.Open(tarPath)
	if err != nil {
		return false
	}
	defer file.Close()

	// Create a new tar reader
	tarReader := tar.NewReader(file)

	// Iterate through the files in the tar archive
	for {
		// Get the next file
		header, err := tarReader.Next()
		if err == io.EOF {
			break // End of tar archive
		}
		if err != nil {
			return false // Error reading tar file
		}

		// Create the full path for the file
		targetPath := filepath.Join(destPath, header.Name)

		// Handle directory
		if header.Typeflag == tar.TypeDir {
			if err := os.MkdirAll(targetPath, os.FileMode(header.Mode)); err != nil {
				return false // Error creating directory
			}
			continue
		}

		// Create the necessary parent directories for the file
		if err := os.MkdirAll(filepath.Dir(targetPath), os.FileMode(0755)); err != nil {
			return false // Error creating directories
		}

		// Create the file
		outFile, err := os.Create(targetPath)
		if err != nil {
			return false // Error creating file
		}
		defer outFile.Close()

		// Copy the content from the tar file to the newly created file
		if _, err := io.Copy(outFile, tarReader); err != nil {
			return false // Error writing to file
		}

		// Set file permissions
		if err := os.Chmod(targetPath, os.FileMode(header.Mode)); err != nil {
			return false // Error setting file permissions
		}
	}

	return true
}
```