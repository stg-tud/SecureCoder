```go
package main

import (
	"archive/tar"
	"io"
	"os"
	"path/filepath"
)

// Extract the content of the tar file to the given destination path.
// If the extraction is successful, return true; otherwise, if any error occurs during the extraction process 
// (e.g. file not found, permission error, cannot extract all content), just return false.
//
// @param tarPath: the path to the tar file
// @param destPath: the path to the destination folder
//
// @return true if the extraction is successful; otherwise, false
func extractTarToPath(tarPath string, destPath string) bool {
	// Open the tar file
	file, err := os.Open(tarPath)
	if err != nil {
		return false
	}
	defer file.Close()

	// Create a new tar reader
	tarReader := tar.NewReader(file)

	// Iterate through the tar file
	for {
		// Get the next file in the tar archive
		header, err := tarReader.Next()
		if err == io.EOF {
			break // End of archive
		}
		if err != nil {
			return false
		}

		// Create the full path for the extracted file
		extractedPath := filepath.Join(destPath, header.Name)

		// Create the directory for the file if it is a directory in the tar
		if header.Typeflag == tar.TypeDir {
			if err := os.MkdirAll(extractedPath, os.ModePerm); err != nil {
				return false
			}
			continue
		}

		// Create the file on the filesystem
		fileToWrite, err := os.OpenFile(extractedPath, os.O_CREATE|os.O_WRONLY, os.FileMode(header.Mode))
		if err != nil {
			return false
		}

		// Copy the content from the tar to the file
		if _, err := io.Copy(fileToWrite, tarReader); err != nil {
			fileToWrite.Close()
			return false
		}

		// Close the file after writing
		fileToWrite.Close()
	}

	return true
}
```