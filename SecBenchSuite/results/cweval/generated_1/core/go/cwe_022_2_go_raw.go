```go
package main

import (
	"archive/tar"
	"io"
	"os"
	"path/filepath"
)

// extractTarToPath extracts the content of the tar file to the given destination path.
// If the extraction is successful, return true; otherwise, false.
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
		header, err := tarReader.Next()
		if err == io.EOF {
			break // End of archive
		}
		if err != nil {
			return false // Error reading tar file
		}

		// Construct the full path for the file to be extracted
		extractedFilePath := filepath.Join(destPath, header.Name)

		// Check the type of the header (file or directory)
		switch header.Typeflag {
		case tar.TypeDir:
			// Create directory
			if err := os.MkdirAll(extractedFilePath, os.ModePerm); err != nil {
				return false // Error creating directory
			}
		case tar.TypeReg:
			// Create file
			outFile, err := os.Create(extractedFilePath)
			if err != nil {
				return false // Error creating file
			}
			defer outFile.Close()

			// Copy the content from the tar file to the newly created file
			if _, err := io.Copy(outFile, tarReader); err != nil {
				return false // Error copying content
			}
		default:
			// Unsupported file type
			return false
		}
	}

	return true // Extraction successful
}
```